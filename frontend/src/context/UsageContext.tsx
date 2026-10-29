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

import { ApiError, getUsage, quotaErrorCode } from "@/services/api";
import type { UsageQuota, UsageResponse } from "@/types/api";

type UsageContextValue = {
  usage: UsageResponse | null;
  isLoading: boolean;
  error: string | null;
  refreshUsage: () => Promise<void>;
  updateQuota: (quota: UsageQuota | null) => void;
  /** Apply the quota state carried by a failed request (user or service-wide limit). */
  noteApiError: (error: unknown) => void;
};

const UsageContext = createContext<UsageContextValue | null>(null);

export function UsageProvider({ children }: { children: ReactNode }) {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshUsage = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setUsage(await getUsage());
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "Usage information unavailable.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refreshUsage();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [refreshUsage]);

  const updateQuota = useCallback(
    (quota: UsageQuota | null) => {
      if (!quota) {
        return;
      }
      if (!usage) {
        void refreshUsage();
        return;
      }
      setUsage((current) => (current ? { ...current, ...quota } : current));
    },
    [refreshUsage, usage],
  );

  const noteApiError = useCallback(
    (requestError: unknown) => {
      if (requestError instanceof ApiError) {
        updateQuota(requestError.usage);
      }
      // The service-wide 429 carries no per-user headers; refetch so
      // usage.service.remaining reflects the exhausted shared allowance.
      if (quotaErrorCode(requestError) === "daily_service_quota_exceeded") {
        void refreshUsage();
      }
    },
    [refreshUsage, updateQuota],
  );

  const value = useMemo(
    () => ({ usage, isLoading, error, refreshUsage, updateQuota, noteApiError }),
    [error, isLoading, noteApiError, refreshUsage, updateQuota, usage],
  );

  return <UsageContext.Provider value={value}>{children}</UsageContext.Provider>;
}

export function useUsage() {
  const context = useContext(UsageContext);
  if (!context) {
    throw new Error("useUsage must be used within UsageProvider");
  }
  return context;
}
