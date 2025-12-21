# Secure Data Agent

A Streamlit-based application for secure, role-based access to multiple SQLite databases, with natural language querying and agent-powered analytics. Supports authentication, rate limiting, visualization, and safe file handling.

---

## Features

- 🔐 **Role-based authentication** (via [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator))
- 🗃️ **Multiple database support** (switch between databases based on user role)
- 🤖 **Agent-powered natural language queries** (integrates with OpenAI models)
- 📊 **Automatic data visualization** (images generated and displayed securely)
- 📝 **Chat history** with download options for generated images
- ⚡ **Rate limiting** and **resource cleanup** for stability
- 🛡️ **Security best practices** (input validation, file/path checks, sensitive config in `.env`)

---

## Quick Start

### 1. Clone the repository

```sh
git clone https://github.com/saadrza/ai_agents_visuals.git
cd ai_agents_visuals
```

### 2. Set up your environment

- Create a `.env` file with your OpenAI API key:
  ```
  OPENAI_API_KEY=your-openai-key
  ```

- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

### 3. Configure authentication

- Use `hasher.py` to generate password hashes for your users.
- Create an `auth.yaml` file in the project root (see [streamlit-authenticator docs](https://github.com/mkhorasani/Streamlit-Authenticator) for format).

### 4. Add your SQLite databases

- Place your `.db` files in the appropriate location in input_files/database folder or setup using config file.
- Update `data/db_registry.py` to register your databases and user access.

### 5. Run the app

```sh
streamlit run app.py
```

---

## Docker

Build and run with Docker:

```sh
docker build -t secure-data-agent .
docker run -p 8501:8501 --env-file .env secure-data-agent
```

---

## Project Structure

```
.
├── app.py                 # Main Streamlit app
├── main.py                # Main without app (works using CLI)
├── test_analysis_tool.py  # Tests checking for OpenAI api, databases, parsing of Prompts, and wroking of agents
├── agent/
│   └── orchestrator.py   # Agent orchestration logic using LangChain
├── data/
│   ├── db_access.py      # Database access helpers
│   └── db_registry.py    # Database registry and user access
├── generated_images/     # Generated visualizations
├── input_files/
│   ├── database          # Folder with Databases
│   └── hasher.py         # Password hash generator (not committed)
├── requirements.txt
├── styles/
│   └── company_styles.py # Company Styles helpers
├── auth.yaml             # Authentication config   (not committed)
├── .env                  # Environment variables   (not committed)
└── .gitignore
```

---

## Security Notes

- **Never commit `.env` or `auth.yaml` to version control.**
- All user input is validated and database access is restricted by role.
- Only SELECT queries are allowed; all other SQL is blocked.

---

## License

MIT License

---

## Credits

- [Streamlit](https://streamlit.io/)
- [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)
- [OpenAI](https://openai.com/)