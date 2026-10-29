import type { Metadata } from "next";
import InitColorSchemeScript from "@mui/material/InitColorSchemeScript";

import { DegreeProvider } from "@/context/DegreeContext";
import { SettingsProvider } from "@/context/SettingsContext";
import { UsageProvider } from "@/context/UsageContext";
import {
  COLOR_SCHEME_MIGRATION_SCRIPT,
  COLOR_SCHEME_STORAGE_KEY,
} from "@/theme/colorScheme";

import { EmotionRegistry } from "./EmotionRegistry";
import "./globals.css";

export const metadata: Metadata = {
  title: "Modulio",
  description: "Study consultant for FU Berlin degree programs.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <script
          suppressHydrationWarning
          dangerouslySetInnerHTML={{ __html: COLOR_SCHEME_MIGRATION_SCRIPT }}
        />
        <InitColorSchemeScript
          attribute="data"
          defaultMode="light"
          modeStorageKey={COLOR_SCHEME_STORAGE_KEY}
        />
        <EmotionRegistry>
          <SettingsProvider>
            <UsageProvider>
              <DegreeProvider>{children}</DegreeProvider>
            </UsageProvider>
          </SettingsProvider>
        </EmotionRegistry>
      </body>
    </html>
  );
}
