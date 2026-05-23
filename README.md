<p align="center">
  <img src="Backend/docs/screenshots/header.png" width="100%" alt="Closira Banner"/>
</p>

<p align="center">
  <strong>An AI-powered customer communication platform for SMBs.</strong><br>
  <em>Features a React Native mobile dashboard and a robust FastAPI backend that intelligently routes messages, automates responses, schedules follow-ups, and manages escalations.</em>
</p>

<br>

Closira is designed with a strong emphasis on production-inspired engineering practices, separating the stack into a zero-config [Frontend App](Frontend/README.md) and an event-sourced [Backend API](Backend/docs/architecture.md).

---

## 🌟 Key Features

*   **Asynchronous Processing:** Non-blocking enquiry ingestion. Expensive tasks (like SOP matching) run via background threads to ensure fast API response times.
*   **Event-Sourced Timeline Audit:** Every state change, SOP match, or manual intervention is immutably logged into a chronological timeline table, ensuring total observability.
*   **Structured JSON Logging:** Fully machine-parseable logs ready for ELK/Datadog ingestion, featuring request correlation IDs (`X-Correlation-ID`) across middleware and execution threads.
*   **Concurrency Race-Condition Guards:** Advanced background task validation prevents stale data overwrites if an agent manually escalates an enquiry mid-processing.
*   **Domain Exception Handling:** Clean architectural boundaries. The service layer throws transport-agnostic domain exceptions (`EnquiryNotFoundError`), leaving the framework layer (`main.py`) to map them to HTTP responses.

---

## 📸 Screenshots

### Mobile App Dashboard
<p align="center">
  <img src="Backend/docs/screenshots/Screenshot_20260523_184230_Frontend.jpg" width="19%" alt="Dashboard Home"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184238_Frontend.jpg" width="19%" alt="Leads List"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184254_Frontend.jpg" width="19%" alt="Conversation Detail"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184303_Frontend.jpg" width="19%" alt="Follow Ups"/>
  <img src="Backend/docs/screenshots/Screenshot_20260523_184310_Frontend.jpg" width="19%" alt="Escalations"/>
</p>

### Architecture & Workflow Diagram
<p align="center">
  <img src="Backend/docs/screenshots/architecture_v2.png" width="100%" alt="Closira Architecture and Workflow"/>
</p>

### API Swagger Documentation
<p align="center">
  <img src="Backend/docs/screenshots/swagger.png" width="100%" alt="Swagger API"/>
</p>

---

## 📂 Project Structure

```text
Closira/
├── Frontend/                 # React Native Mobile Dashboard (Expo)
│   ├── components/           # Reusable UI cards and badges
│   ├── constants/            # Design system (colors, typography)
│   ├── mock/                 # Local JSON data (no backend needed)
│   ├── navigation/           # Bottom tabs and stack navigation
│   └── screens/              # Dashboard, Leads, Escalations views
├── Backend/                  # FastAPI Python Backend
│   ├── app/                  # Main application, ORM, routers, services
│   ├── docs/                 # Architecture & Demo documentation
│   ├── tests/                # Unit testing
│   └── verify_backend.py     # End-to-End automated validation script
└── README.md
```

---

## 🚀 Getting Started

The project is split into two runnable environments.

### 📱 1. Mobile App (Frontend)
A fully modular React Native dashboard using local mock data.

1. **Navigate to the frontend**
   ```bash
   cd Frontend
   ```
2. **Install & Run**
   ```bash
   npm install
   npx expo start
   ```
*(For detailed UI notes, see the [Frontend README](Frontend/README.md))*

---

### ⚙️ 2. API Server (Backend)

*   **Prerequisites:** Python 3.10+

#### Local Setup

1. **Clone the repository and enter the Backend directory**
   ```bash
   cd Backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the API Server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **View Swagger Documentation**
   Open your browser to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Verification & Testing

The project includes a robust End-to-End (E2E) automated verification script that tests:
*   Root and Health metadata endpoints.
*   Global validation schemas and custom 404 domain exceptions.
*   The complete async lifecycle (Creation → SOP Match → Qualification).
*   Concurrency protection (Manual escalations during async sleep).
*   Chronological event sorting and query filtering bounds.

Run the test suite against a live server:
```bash
python verify_backend.py
```

---

## 📚 Documentation

For deeper dives into the system design and how to run a live demo:
*   [Architecture Documentation](Backend/docs/architecture.md) — Explains the request lifecycle, scalability tradeoffs, and background task safety.
*   [Demo Walkthrough Guide](Backend/docs/demo_walkthrough.md) — A step-by-step guide for testing the API workflows in Swagger.

---

## ⚙️ Engineering Decisions & Tradeoffs

To fit within the scope of an internship project while maintaining high architectural standards, several practical tradeoffs were made:

*   **SQLite over PostgreSQL:** Used for simplicity and zero-configuration local setup. To account for this, the app uses indexes carefully and keeps transaction windows short.
*   **In-Memory BackgroundTasks over Celery/Redis:** Used to avoid infrastructure bloat. To make this safe, explicit race condition guards and database rollbacks are implemented inside the task workers.
*   **Static Mock SOPs over LLMs:** The `mock_sops` module uses a pure, deterministic keyword matcher. This isolates the logic cleanly, making it extremely easy to swap out with an external OpenAI/LLM call in the future without breaking the router or service layers.
