# MLHKS - Medicine Error Detection Companion

A sophisticated AI-powered healthcare application that analyzes patient medical data and documents to detect potential drug interactions, side effects, and provides personalized medical insights.

## 🎯 Overview

MLHKS (Medicine Error Detection Companion) is an intelligent healthcare assistant that combines patient medical history, current medications, and uploaded medical documents to provide comprehensive analysis of potential drug interactions and side effects. The system uses advanced AI agents to extract drug information, analyze chemical interactions, and generate patient-friendly medical insights.

## ✨ Features

- **Multi-format Document Processing**: Supports PDF and DOCX medical document analysis
- **Drug Interaction Analysis**: Advanced chemical structure analysis using SMILES representations
- **AI-Powered Insights**: Multi-agent AI system for comprehensive medical analysis
- **Patient-Friendly Output**: Clear, non-frightening explanations with doctor consultation questions
- **Web Interface**: Both Streamlit and FastAPI-based interfaces available
- **Comprehensive Medical Database**: Integration with drug interaction databases

## 🏗️ Architecture

### Core Components

1. **Data Models**: Pydantic-based patient data validation and structure
2. **Document Processing Engine**: PDF/DOCX text extraction and processing
3. **AI Agent System**: Multi-stage analysis using SmoLAgents framework
4. **Database Layer**: SQLite database with drug interaction data
5. **API Service**: FastAPI-based REST endpoints
6. **Frontend Interfaces**: Streamlit web application

### AI Agent Pipeline

1. **Entity Extraction Agent**: Extracts drug names from patient data and documents
2. **Drug Analysis Agent**: Converts drug names to chemical structures (SMILES)
3. **Interaction Analysis**: Queries database for drug pair interactions
4. **Summary Agent**: Synthesizes findings into actionable insights

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Raman369AI/mlhks.git
   cd mlhks
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Initialize Database** (if not already present):
   The application uses a SQLite database (`raman.db`) for drug interaction data.

## 🎮 Usage

### FastAPI Web Service

1. **Start the API server**:
   ```bash
   uvicorn patient_help_api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Main endpoint: `POST /process-patient-data/`

### Streamlit Web Interface

1. **Run the Streamlit app**:
   ```bash
   streamlit run app1.py
   ```

2. **Access the web interface**:
   - Open http://localhost:8501 in your browser

### API Usage Example

```python
import requests

# Patient data
payload = {
    "age": 45,
    "sex": "Male",
    "height": 175,
    "weight": 85,
    "allergies": "Shellfish, Dust",
    "preexisting_conditions": "Diabetes, Hypertension",
    "medications": "Aspirin, Atorvastatin",
    "family_history": "Heart Disease",
    "question": "I feel dizzy after taking my medication. What could be wrong?"
}

# Upload medical documents (optional)
files = [
    ('files', ('medical_report.pdf', open('medical_report.pdf', 'rb'), 'application/pdf'))
]

# Make request
response = requests.post(
    "http://localhost:8000/process-patient-data/",
    data=payload,
    files=files
)

print(response.json())
```

## 📋 API Reference

### POST /process-patient-data/

Analyzes patient data and uploaded medical documents to provide medical insights.

**Request Parameters:**
- `age` (int): Patient age
- `sex` (str): Patient sex (Male/Female/Other)
- `height` (float): Height in cm
- `weight` (float): Weight in kg
- `allergies` (str): Known allergies
- `preexisting_conditions` (str): Medical conditions
- `medications` (str): Current medications
- `family_history` (str): Family medical history
- `question` (str): Patient's medical question
- `files` (list): Medical documents (PDF/DOCX)

**Response:**
```json
{
  "insights": "Detailed medical analysis and recommendations..."
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for AI processing | Yes |

### Database Configuration

The application uses SQLite for drug interaction data. The database schema includes:
- Drug pairs with SMILES representations
- Side effect classifications
- Interaction severity levels

## 📊 Data Sources

- **Drug Database**: Based on DrugBank and TWOSIDES datasets
- **Chemical Structures**: PubChemPy integration for SMILES conversion
- **Side Effects**: Comprehensive database with 1300+ side effect categories

## 🛡️ Security Considerations

- **API Keys**: Never commit API keys to version control
- **Patient Data**: Ensure compliance with healthcare privacy regulations
- **File Uploads**: Temporary files are automatically cleaned up
- **Input Validation**: Comprehensive input sanitization and validation

## 🧪 Testing

Run the test payload example:
```bash
jupyter notebook test_payload.ipynb
```

Or test with curl:
```bash
curl -X POST "http://localhost:8000/process-patient-data/" \
  -F "age=45" \
  -F "sex=Male" \
  -F "height=175" \
  -F "weight=85" \
  -F "allergies=Shellfish, Dust" \
  -F "preexisting_conditions=Diabetes, Hypertension" \
  -F "medications=Aspirin, Atorvastatin" \
  -F "family_history=Heart Disease" \
  -F "question=I feel dizzy after taking my medication. What could be wrong?"
```

## 🐳 Docker Deployment

Build and run with Docker:
```bash
docker build -t mlhks .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_api_key mlhks
```

## 📁 Project Structure

```
mlhks/
├── app1.py                     # Streamlit web interface
├── patient_help_api.py         # Main FastAPI application
├── patient_help.py             # Alternative API implementation
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── README.md                  # This file
├── raman.db                   # SQLite database
├── documents_uploaded/        # Sample medical documents
├── test_payload.ipynb         # Testing notebook
├── new.ipynb                  # Development notebook
└── temp/                      # Temporary file storage
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure `raman.db` file exists and is accessible
   - Check file permissions

2. **API Key Issues**:
   - Verify your Gemini API key is valid
   - Check environment variable configuration

3. **File Upload Errors**:
   - Ensure uploaded files are PDF or DOCX format
   - Check file size limits

4. **Memory Issues**:
   - Large document processing may require additional memory
   - Consider processing documents in batches

### Logging

Enable detailed logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## ⚠️ Disclaimers

- **Medical Advice**: This tool is for informational purposes only and does not replace professional medical advice
- **Accuracy**: Always consult healthcare providers for medical concerns
- **Liability**: Users are responsible for verifying all medical information

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review common troubleshooting steps

## 🙏 Acknowledgments

- DrugBank and TWOSIDES datasets for drug interaction data
- SmoLAgents framework for AI agent orchestration
- Google Gemini for AI-powered analysis
- FastAPI and Streamlit communities for excellent frameworks

---

**Note**: This is a research and development project. Always consult qualified healthcare professionals for medical decisions.