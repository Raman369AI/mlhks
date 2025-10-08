from fastapi import FastAPI, HTTPException,File,UploadFile,Form
from pydantic import BaseModel, Field
from typing import List, Optional
import requests
import fitz
from docx2python import docx2python
import sqlite3
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import tempfile
import asyncio
from fastapi.background import BackgroundTasks
from smolagents import CodeAgent, LiteLLMModel, tool
import itertools
import pubchempy as pcp
import traceback
import spacy
from spacy.language import Language
from spacy.tokens import Span
from spacy.util import filter_spans
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse





# Define the Pydantic model for Patient data
class Patient(BaseModel):
    age: int = Field( ge=0, description="Age of the patient")
    sex: str = Field( pattern="^(Male|Female|Other)$", description="Sex of the patient")
    height: float = Field( gt=0, description="Height in cm")
    weight: float = Field( gt=0, description="Weight in kg")
    allergies: Optional[str] = Field(default="", description="List of allergies")
    preexisting_conditions: Optional[str] = Field(default="", description="List of preexisting medical conditions")
    medications: Optional[str] = Field(default="", description="List of current medications")
    family_history: Optional[str] = Field(default="", description="Family medical history")
    question: str = Field( description="The question or issue the patient wants help with")
    user_document_data: Optional[str] = Field(default="", description="Extracted text from uploaded documents")

@tool
def connect_to__db() -> str:
    """
    Returns:
    str: A success message indicating the connection was established.
    """
    try:
        conn = sqlite3.connect('/home/kronos/Desktop/mlhks/raman.db')
        conn.close()
        return "Successfully connected to the database."
    except sqlite3.Error as e:
        return f"An error occurred: {e}"

@tool
def create_pairs(li: list) -> list:
    """
    Creates pairs of drugs from the input list and converts each drug to its SMILES representation.
    
    Args:
        li: A list containing the names of the drugs.
        
    Returns:
        list: A list of tuples, each containing a pair of drugs with their SMILES representations.
              Only includes pairs where both drugs have valid SMILES.
    """

    
    def name_to_smiles(drug_name):
        compounds = pcp.get_compounds(drug_name, 'name')
        if compounds:
            return compounds[0].canonical_smiles
        return None
    
    # Convert drug names to (name, SMILES) pairs
    drug_smiles = []
    for drug in li:
        smiles = name_to_smiles(drug)
        if smiles:  # Only add drugs with valid SMILES
            drug_smiles.append(smiles)
    
    # Create all possible pairs from valid drugs
    pairs = list(itertools.combinations(drug_smiles, 2))
    return pairs
@tool
def search_for_sideeffects(lis: list) -> str:
    """
    Searches for side effects of drug pairs in a database.    
    Args:
        lis: A list containing the names of the drugs.
        
    Returns:
        str:  string containing the side effects for each drug pair.
    """
    import sqlite3
    p = []
    for i in lis:
        try:
            conn = sqlite3.connect('/home/kronos/Desktop/mlhks/raman.db')
            cursor = conn.cursor()
            cursor.execute('''select Y from raman where Drug1 = ? and Drug2 = ?''', (i[0], i[1]))
            rows = cursor.fetchall()
            for row in rows:
                p.append(str(row[0])) 
            conn.close()
        except sqlite3.Error as e:
            return f"An error occurred: {e}"
    return  ','.join(p)

# Initialize FastAPI
app = FastAPI(debug=True)
origins = [
    "http://localhost:3000",  #  The origin of your React app (port 3000 is common for Create React App)
    "http://127.0.0.1:3000", #  Include this as well
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  #  Allow requests from your React app's origin
    allow_credentials=True,
    allow_methods=["*"],  #  Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  #  Allow all headers
)
def extract_text_from_pdf(file_path: str) -> str:
    try:
        pdf_document = fitz.open(file_path)
        all_text = ""
        for page in pdf_document:
            all_text += page.get_text() + "\n"
        pdf_document.close()
        return all_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")


def extract_text_from_word(file_path: str) -> str:
    try:
        doc_content = docx2python(file_path)
        return doc_content.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from Word document: {str(e)}")

# Mock function to interact with the fine-tuned Gemini LLM
# def query_gemini_llm(prompt: str, context: dict) -> str:
#     # Replace this with actual API call to Gemini LLM
#     llm_input = {
#         "prompt": prompt,
#         "context": context
#     }
#     try:
#         response = requests.post("http://gemini-llm-api-url.com/query", json=llm_input,timeout=10)
#         response.raise_for_status()
#         return response.json().get("completion", "No response from LLM")
#     except requests.exceptions.RequestException as e:
#         # Catch all exceptions related to the API call (e.g., connection errors, timeouts)
#         raise HTTPException(status_code=503, detail=f"Error querying Gemini LLM: {str(e)}")
                                                                                                                  



@app.post("/process-patient-data/")
async def process_patient_data(
    background_tasks: BackgroundTasks,
    age: int = Form(...),
    sex: str = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    allergies: str = Form(...),
    preexisting_conditions: str = Form(...),
    medications: str = Form(...),
    family_history: str = Form(...),
    question: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        extracted_texts = []
        temp_files = []

        if files:
            for file in files:
                # Create a temporary file with a unique name
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
                    temp_file_path = temp.name
                    temp_files.append(temp_file_path)
                    
                    # Write content to the temporary file
                    content = await file.read()
                    temp.write(content)
                
                # Process the file after the file handle is closed
                try:
                    if file.filename.endswith(".pdf"):
                        extracted_texts.append(extract_text_from_pdf(temp_file_path))
                    elif file.filename.endswith(".docx"):
                        extracted_texts.append(extract_text_from_word(temp_file_path))
                    else:
                        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")
                except Exception as e:
                    print(f"Error processing file {file.filename}: {e}")
        
        # Add cleanup task to run in the background
        background_tasks.add_task(cleanup_temp_files, temp_files)
        
        combined_texts = "\n".join(extracted_texts)
        
        # Create Patient object
        patient_data = Patient(
            age=age,
            sex=sex,
            height=height,
            weight=weight,
            allergies=allergies,
            preexisting_conditions=preexisting_conditions,
            medications=medications,
            family_history=family_history,
            question=question,
            user_document_data=combined_texts,
        )
        
        print("Patient data:", patient_data.dict())


        context = patient_data.dict(exclude={"question"})
        prompt = patient_data.question
        
        model = LiteLLMModel(model_id="gemini/gemini-2.0-flash", api_key=os.getenv("GEMINI_API_KEY"), temperature=0.1)
        agent = CodeAgent(tools = [],model=model, name="Entity extraction Agent", description="Extracts medical drug entities from text and give it as a list.")
        #The input to the agent from the user
        result = agent.run(f'''You are a highly capable AI medical assistant supported by a statistical tool that provides 100% accurate detection of drug interactions, contraindications, and allergy conflicts.
Consider the following patient context: {context}, which includes structured patient data, previous surgical records, prescribed medications, allergies, and diagnoses.
The patient's question is: {prompt}
Your task is to:
Analyze the full context thoroughly, including past medical history and current medications.
Identify and explain any possible causes for the patient's concern, based on side effects, allergies, medication interactions, or prior surgical outcomes.
If there are any potential risks, medication conflicts, or red flags, describe them clearly and in detail.
At the end of your response, provide a list of clear, patient-friendly questions the patient should ask their doctor during their next consultation.
Be detailed, medically accurate, and empathetic. Ensure the output helps the patient better understand their condition and prepare for a meaningful discussion with their healthcare provider.''')
        li = agent.memory.steps[-1].action_output
       # li = extract_drugs(medications)
        print("Extracted drugs:", li)

        if li:

            main_agent = CodeAgent(tools=[create_pairs,search_for_sideeffects], model=model,name="Final Agent", description="use the create_pairs tool first and then take the output of this tool and give it as an input to search  search_for_sideeffects")
            main_agent.run('use the create_pairs tool first and then take the output of this tool and give it as an input to search  search_for_sideeffects', additional_args={"li": li})
            summary_agent = CodeAgent(tools=[], model=model,name="Summary agent", description="You are an agent synthesizing the output of the final agent.\
                                You are to return the side effects of the drugs in the pairs in a user friendly manner and do not frighten the patient\
                                just warn him of the potential side affects. Enrich the content with your knowledge")
                
            lin = main_agent.memory.steps[-1].action_output
            output=summary_agent.run(f" You should return an output as JSON, if output is NOne return the logs as output {main_agent.memory.steps[-1].action_output} is the possible side affects for the drugs that the patient has been taking and it has been  synthsized from FDA data within the drugs mentioned \
                  in {li}, use the {li} to mention the drug names and give a \
                  aprise the paitent by advocating the risks involved in a manner that \
                  is easier to understand and not frightening and also give him questions he can take back to the doctor and this entire thing has to be my final answer and you will start this like a human speaking")
            # The output to be displayed to the user
            output = summary_agent.memory.steps[-1].action_output

            

            return output

    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
    # try:
    #     llm_result = query_gemini_llm(prompt=prompt, context=context)
    #     return {"response": llm_result}
    # except HTTPException as e:
    #     return {"error": e.detail}

async def cleanup_temp_files(temp_files: List[str]):
    # Initial delay to ensure files are released
    await asyncio.sleep(5)
    
    for temp_file in temp_files:
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Deleted temporary file: {temp_file}")
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed to delete {temp_file}: {e}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Failed to delete temporary file after {max_attempts} attempts: {temp_file}")
                    

                                                                                    
