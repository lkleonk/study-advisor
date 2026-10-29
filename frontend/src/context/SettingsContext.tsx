"use client";

import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, useColorScheme } from "@mui/material/styles";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { COLOR_SCHEME_STORAGE_KEY } from "@/theme/colorScheme";
import { appTheme } from "@/theme/theme";
import { DEV_TOOLS_ENABLED } from "@/config/publicConfig";
import {
  COURSE_REGISTRY_PREVIEW_STORAGE_KEY,
  STUDY_PLAN_PREVIEW_STORAGE_KEY,
  TRACING_ENABLED_STORAGE_KEY,
} from "@/app/consultant/components/storage";

type SettingsContextValue = {
  darkMode: boolean;
  toggleDarkMode: () => void;
  tracingEnabled: boolean;
  setTracingEnabled: (enabled: boolean) => void;
  courseRegistryPreviewEnabled: boolean;
  setCourseRegistryPreviewEnabled: (enabled: boolean) => void;
  studyPlanPreviewEnabled: boolean;
  setStudyPlanPreviewEnabled: (enabled: boolean) => void;
};

const SettingsContext = createContext<SettingsContextValue | null>(null);
export function SettingsProvider({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider
      theme={appTheme}
      defaultMode="light"
      modeStorageKey={COLOR_SCHEME_STORAGE_KEY}
      disableTransitionOnChange
    >
      <CssBaseline enableColorScheme />
      <SettingsStateProvider>{children}</SettingsStateProvider>
    </ThemeProvider>
  );
}

function SettingsStateProvider({ children }: { children: ReactNode }) {
  const { mode, setMode } = useColorScheme();
  const darkMode = mode === "dark";
  const [tracingEnabled, setTracingEnabled] = useState(true);
  const [courseRegistryPreviewEnabled, setCourseRegistryPreviewEnabled] = useState(false);
  const [studyPlanPreviewEnabled, setStudyPlanPreviewEnabled] = useState(false);
  const hasReadStoredSettings = useRef(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      // Only an explicit "false" opts out; anything else keeps the default.
      setTracingEnabled(window.localStorage.getItem(TRACING_ENABLED_STORAGE_KEY) !== "false");
      if (DEV_TOOLS_ENABLED) {
        setCourseRegistryPreviewEnabled(
          window.localStorage.getItem(COURSE_REGISTRY_PREVIEW_STORAGE_KEY) === "true",
        );
        setStudyPlanPreviewEnabled(
          window.localStorage.getItem(STUDY_PLAN_PREVIEW_STORAGE_KEY) === "true",
        );
      }
      hasReadStoredSettings.current = true;
    }, 0);

    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!hasReadStoredSettings.current) {
      return;
    }
    window.localStorage.setItem(TRACING_ENABLED_STORAGE_KEY, String(tracingEnabled));
  }, [tracingEnabled]);

  useEffect(() => {
    if (!hasReadStoredSettings.current || !DEV_TOOLS_ENABLED) {
      return;
    }
    window.localStorage.setItem(
      COURSE_REGISTRY_PREVIEW_STORAGE_KEY,
      String(courseRegistryPreviewEnabled),
    );
  }, [courseRegistryPreviewEnabled]);

  useEffect(() => {
    if (!hasReadStoredSettings.current || !DEV_TOOLS_ENABLED) {
      return;
    }
    window.localStorage.setItem(STUDY_PLAN_PREVIEW_STORAGE_KEY, String(studyPlanPreviewEnabled));
  }, [studyPlanPreviewEnabled]);

  const value = useMemo(
    () => ({
      darkMode,
      toggleDarkMode: () => setMode(darkMode ? "light" : "dark"),
      tracingEnabled,
      setTracingEnabled,
      courseRegistryPreviewEnabled,
      setCourseRegistryPreviewEnabled,
      studyPlanPreviewEnabled,
      setStudyPlanPreviewEnabled,
    }),
    [courseRegistryPreviewEnabled, darkMode, setMode, studyPlanPreviewEnabled, tracingEnabled],
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within SettingsProvider");
  }
  return context;
}
