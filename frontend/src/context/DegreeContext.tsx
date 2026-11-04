"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getDegrees } from "@/services/api";
import type { DegreeInfo } from "@/types/api";

export const DEGREE_STORAGE_KEY = "fu-consultant-degree";
export const DEFAULT_DEGREE_ID = "msc_informatik";

// Shown until GET /api/degrees answers; keep in sync with the backend registry (same order).
const FALLBACK_DEGREES: DegreeInfo[] = [
  {
    id: "bsc_informatik",
    display_name: "B.Sc. Informatik",
    regulation: "2023 Studien- und Pruefungsordnung (FU-Mitteilungen 23/2023)",
    plan_validation_enabled: false,
  },
  {
    id: "bsc_bioinformatik",
    display_name: "B.Sc. Bioinformatik",
    regulation: "2023 Studien- und Pruefungsordnung (FU-Mitteilungen 34/2023)",
    plan_validation_enabled: false,
  },
  {
    id: "bsc_physik",
    display_name: "B.Sc. Physik",
    regulation: "2024 Studien- und Pruefungsordnung (FU-Mitteilungen 12/2024)",
    plan_validation_enabled: false,
  },
  {
    id: DEFAULT_DEGREE_ID,
    display_name: "M.Sc. Informatik",
    regulation: "2014 Studien- und Pruefungsordnung",
    plan_validation_enabled: true,
  },
  {
    id: "msc_data_science",
    display_name: "M.Sc. Data Science",
    regulation: "2021 Studien- und Pruefungsordnung (FU-Mitteilungen 18/2021)",
    plan_validation_enabled: false,
  },
  {
    id: "msc_computational_sciences",
    display_name: "M.Sc. Computational Sciences",
    short_name: "M.Sc. Comp. Sciences",
    regulation: "2025 Studien- und Pruefungsordnung (FU-Mitteilungen 21/2025), amended 2026 (27/2026)",
    plan_validation_enabled: false,
  },
  {
    id: "msc_physik",
    display_name: "M.Sc. Physik",
    regulation: "2024 Studien- und Pruefungsordnung (FU-Mitteilungen 12/2024)",
    plan_validation_enabled: false,
  },
];

export type DegreeGroup = { label: string; degrees: DegreeInfo[] };

const DEGREE_LEVELS = [
  { prefix: "bsc_", label: "Bachelor" },
  { prefix: "msc_", label: "Master" },
];

/** Groups degrees by level (from the id prefix), keeping the registry order within each group. */
export function groupDegreesByLevel(degrees: DegreeInfo[]): DegreeGroup[] {
  const groups = DEGREE_LEVELS.map(({ prefix, label }) => ({
    label,
    degrees: degrees.filter((degree) => degree.id.startsWith(prefix)),
  }));
  const other = degrees.filter((degree) => !DEGREE_LEVELS.some(({ prefix }) => degree.id.startsWith(prefix)));
  return [...groups, { label: "Other", degrees: other }].filter((group) => group.degrees.length > 0);
}

type DegreeContextValue = {
  /** Chosen degree id, or null until the user has picked one. */
  degreeId: string | null;
  /** Chosen degree id with the default applied; safe for API calls. */
  effectiveDegreeId: string;
  degrees: DegreeInfo[];
  degreesLoaded: boolean;
  selectDegree: (degreeId: string) => void;
};

const DegreeContext = createContext<DegreeContextValue | null>(null);

export function DegreeProvider({ children }: { children: ReactNode }) {
  const [degreeId, setDegreeId] = useState<string | null>(null);
  const [degrees, setDegrees] = useState<DegreeInfo[]>(FALLBACK_DEGREES);
  const [degreesLoaded, setDegreesLoaded] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDegreeId(window.localStorage.getItem(DEGREE_STORAGE_KEY));
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(async () => {
      try {
        const fetched = await getDegrees();
        if (!cancelled && fetched.length > 0) {
          setDegrees(fetched);
        }
      } catch {
        // Keep the fallback list; the backend list is only for display options.
      } finally {
        if (!cancelled) {
          setDegreesLoaded(true);
        }
      }
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, []);

  const selectDegree = useCallback((nextDegreeId: string) => {
    window.localStorage.setItem(DEGREE_STORAGE_KEY, nextDegreeId);
    setDegreeId(nextDegreeId);
  }, []);

  const value = useMemo(
    () => ({
      degreeId,
      effectiveDegreeId: degreeId ?? DEFAULT_DEGREE_ID,
      degrees,
      degreesLoaded,
      selectDegree,
    }),
    [degreeId, degrees, degreesLoaded, selectDegree],
  );

  return <DegreeContext.Provider value={value}>{children}</DegreeContext.Provider>;
}

export function useDegree() {
  const context = useContext(DegreeContext);
  if (!context) {
    throw new Error("useDegree must be used within DegreeProvider");
  }
  return context;
}
