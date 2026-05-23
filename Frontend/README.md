# Closira Mobile Dashboard

A production-quality React Native (Expo) frontend for the Closira customer communication platform.

## Features
* **Dashboard:** At-a-glance metrics for new leads, follow-ups, and escalations.
* **Leads Inbox:** Unified list of inbound inquiries across WhatsApp, Email, and Calls.
* **Escalations View:** High-urgency alerts requiring human intervention.
* **Conversation Threading:** Deep-dive into specific conversations, complete with AI summaries, SOP match badges, and chronological event timelines.
* **SaaS Design System:** Clean, light-themed mobile UI optimized for business owners.

---

## 🚀 Getting Started

### Prerequisites
* Node.js (v18+)
* Expo CLI (`npm install -g expo-cli`)
* Expo Go app on your iOS/Android device (optional but recommended)

### Installation & Run

1. Navigate to the frontend directory:
   ```bash
   cd Frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Expo development server:
   ```bash
   npx expo start
   ```

4. **To view the app:**
   * Open the **Expo Go** app on your phone and scan the QR code printed in your terminal.
   * Or press `i` in the terminal to open an iOS simulator.
   * Or press `a` to open an Android emulator.

---

## 🎨 Styling Decisions

Per the project requirements, a custom Design System using `StyleSheet` was implemented. 
While NativeWind (Tailwind for React Native) was considered, the latest Expo SDK 53 template setup combined with NativeWind v4 often requires complex babel configuration that can lead to fragile local builds. 

To guarantee a **zero-configuration, instantly runnable** repository for recruiters, pure `StyleSheet` was utilized. All design tokens (colors, spacing, typography) are centralized in `constants/colors.js` to perfectly mimic a clean, utility-first SaaS aesthetic.

---

## 📂 Architecture

* `/screens`: Full-page views (Home, Leads, Escalations, Conversation Detail).
* `/components`: Highly reusable UI elements (Cards, Badges, Empty States).
* `/navigation`: React Navigation stack and bottom tab configurations.
* `/mock`: Hardcoded structured JSON data to simulate the backend.
* `/constants`: The centralized design system (theme).

**Note:** This application is completely frontend-only and relies on local JSON mock data. There is no active backend connection, authentication, or live API usage.
