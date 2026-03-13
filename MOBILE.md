# 📱 CodeGenie Mobile App — Migration Guide

> **Approach:** Keep the existing desktop codebase intact. Add mobile support alongside it using **Capacitor** + platform-aware components.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Shared React Codebase               │
│         (App.jsx, ChatPanel, services)           │
├────────────────┬────────────────┬────────────────┤
│   Desktop      │    Web         │    Mobile      │
│   (Electron)   │   (Browser)    │  (Capacitor)   │
│   Monaco ✅    │   Monaco ✅    │  CodeMirror ✅  │
│   File dialogs │   REST API     │  Touch UI      │
│   .dmg/.exe    │   Vite dev     │  .apk/.ipa     │
└────────────────┴────────────────┴────────────────┘
```

**Key Principle:** Monaco stays for desktop & web. CodeMirror is added only for mobile. A platform-aware editor component auto-selects the right one.

---

## Step 1 — Install Capacitor

```bash
cd frontend
npm install @capacitor/core @capacitor/cli
npx cap init "CodeGenie" "com.codegenie.editor" --web-dir dist

# Add platforms
npm install @capacitor/ios @capacitor/android
npx cap add ios
npx cap add android

# Mobile plugins
npm install @capacitor/filesystem @capacitor/keyboard
npm install @capacitor/status-bar @capacitor/haptics @capacitor/share
```

---

## Step 2 — Add Platform Detection

**New file:** `src/utils/platform.js`

```js
export const isElectron = () =>
    typeof window !== 'undefined' && !!window.electronAPI;

export const isCapacitor = () =>
    typeof window !== 'undefined' && !!window.Capacitor;

export const isMobile = () => isCapacitor();
export const isDesktop = () => isElectron();
export const isWeb = () => !isElectron() && !isCapacitor();
```

---

## Step 3 — Create Adaptive Editor Component

Install CodeMirror (for mobile only):
```bash
npm install @uiw/react-codemirror @codemirror/lang-javascript @codemirror/lang-python
```

**New file:** `src/components/AdaptiveEditor.jsx`

```jsx
import { isMobile } from '../utils/platform';
import { lazy, Suspense } from 'react';

// Lazy load — only loads the editor needed for the platform
const MonacoEditor = lazy(() => import('./editors/MonacoEditorWrapper'));
const MobileEditor = lazy(() => import('./editors/MobileEditorWrapper'));

export default function AdaptiveEditor(props) {
    return (
        <Suspense fallback={<div className="editor-loading">Loading editor...</div>}>
            {isMobile() ? <MobileEditor {...props} /> : <MonacoEditor {...props} />}
        </Suspense>
    );
}
```

**New file:** `src/components/editors/MonacoEditorWrapper.jsx`
> Wraps your existing Monaco editor (no changes to current code)

```jsx
import Editor from "@monaco-editor/react";

export default function MonacoEditorWrapper({ code, language, onChange, theme }) {
    return (
        <Editor
            height="100%"
            language={language || "javascript"}
            theme={theme || "vs-dark"}
            value={code}
            onChange={onChange}
            options={{
                minimap: { enabled: true },
                fontSize: 14,
                wordWrap: "on",
                automaticLayout: true,
            }}
        />
    );
}
```

**New file:** `src/components/editors/MobileEditorWrapper.jsx`
> Touch-friendly editor for mobile

```jsx
import CodeMirror from "@uiw/react-codemirror";
import { javascript } from "@codemirror/lang-javascript";
import { python } from "@codemirror/lang-python";

const langExtensions = { javascript, python };

export default function MobileEditorWrapper({ code, language, onChange }) {
    const ext = langExtensions[language] || javascript;
    return (
        <CodeMirror
            value={code}
            height="100%"
            theme="dark"
            extensions={[ext()]}
            onChange={onChange}
            style={{ fontSize: '16px' }}  /* Larger for touch */
        />
    );
}
```

**Then in `EditorPanel.jsx`** — replace the direct Monaco import with AdaptiveEditor:
```jsx
// Change this ONE import line:
// import Editor from "@monaco-editor/react";
import AdaptiveEditor from "./AdaptiveEditor";

// Use <AdaptiveEditor .../> instead of <Editor .../> in the JSX
```

> ✅ Desktop users get Monaco (unchanged). Mobile users get CodeMirror.

---

## Step 4 — Responsive CSS

Add to `src/App.css` (keep existing styles, add these):

```css
/* ── Mobile layout ── */
@media (max-width: 768px) {
    .app-container {
        flex-direction: column;
    }
    .sidebar {
        width: 100%;
        height: 48px;
        flex-direction: row;
        overflow-x: auto;
    }
    .sidebar .icon-btn {
        min-width: 48px;
        min-height: 48px;  /* Touch target */
    }
    .editor-area {
        height: 50vh;
    }
    .chat-panel {
        height: 50vh;
        width: 100%;
    }
    .panel-tabs {
        font-size: 14px;
    }
}
```

---

## Step 5 — Platform-Aware File Operations

Update file open/save in `App.jsx` to support all platforms:

```jsx
import { isElectron, isCapacitor, isWeb } from './utils/platform';

const handleOpenFile = async () => {
    if (isElectron()) {
        // Existing Electron file dialog (unchanged)
        const result = await window.electronAPI.openFile();
        if (result) { /* ... existing code ... */ }
    } else if (isCapacitor()) {
        // Mobile: use Capacitor Filesystem
        const { Filesystem, Directory } = await import('@capacitor/filesystem');
        // Mobile file picker logic
    } else {
        // Web: use File System Access API
        const [handle] = await window.showOpenFilePicker();
        const file = await handle.getFile();
        const content = await file.text();
        // ... set content
    }
};
```

---

## Step 6 — Backend Connection

Your FastAPI backend stays the same. Just configure the API URL:

```js
// src/services/api.js
const getBaseURL = () => {
    if (isElectron()) return 'http://localhost:8000/api';  // Bundled backend
    if (isCapacitor()) return 'https://your-backend.onrender.com/api'; // Deployed
    return '/api';  // Web (proxied by Vite)
};
```

---

## Step 7 — Build & Run

```bash
# Desktop (unchanged)
npm run electron:dev        # Dev
npm run electron:build      # Build .dmg/.exe

# Mobile
npm run build               # Build React to dist/
npx cap sync                # Copy to native projects
npx cap open ios            # Open in Xcode
npx cap open android        # Open in Android Studio

# Web (unchanged)
npm run dev
```

---

## Step 8 — Mobile CI/CD (GitHub Actions)

**New file:** `.github/workflows/mobile-build.yml`

```yaml
name: Build Mobile App
on:
  push:
    tags: ['v*']

jobs:
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '22' }
      - uses: actions/setup-java@v4
        with: { java-version: '17', distribution: 'temurin' }
      - run: cd frontend && npm ci && npm run build && npx cap sync android
      - run: cd frontend/android && ./gradlew assembleDebug
      - uses: actions/upload-artifact@v4
        with:
          name: android-apk
          path: frontend/android/app/build/outputs/apk/debug/*.apk
```

---

## New Files Summary

| File | Purpose |
|---|---|
| `src/utils/platform.js` | Detect Electron / Capacitor / Web |
| `src/components/AdaptiveEditor.jsx` | Auto-selects Monaco or CodeMirror |
| `src/components/editors/MonacoEditorWrapper.jsx` | Existing Monaco (extracted) |
| `src/components/editors/MobileEditorWrapper.jsx` | CodeMirror for mobile |
| `capacitor.config.ts` | Capacitor config (auto-generated) |
| `ios/` | iOS native project (auto-generated) |
| `android/` | Android native project (auto-generated) |

---

## ⚠️ Key Notes

| Topic | Detail |
|---|---|
| **Monaco stays** | Desktop & web keep Monaco as-is |
| **CodeMirror added** | Only loads on mobile (lazy-loaded) |
| **No code deleted** | Everything is additive |
| **Backend unchanged** | Same FastAPI, mobile uses deployed URL |
| **iOS App Store** | Needs Apple Developer account ($99/yr) |
| **Android APK** | Can sideload free, Play Store = $25 one-time |
