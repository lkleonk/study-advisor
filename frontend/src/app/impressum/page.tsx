import type { Metadata } from "next";

import {
  LegalConfigurationNotice,
  LegalPageShell,
  LegalSection,
} from "@/components/LegalPageShell";
import { ObfuscatedEmail } from "@/components/ObfuscatedEmail";
import { isLegalContactConfigured, legalContact } from "@/config/legalContact";

export const metadata: Metadata = {
  title: "Impressum | Modulio",
  description: "Anbieterkennzeichnung für Modulio.",
};

export default function ImpressumPage() {
  return (
    <LegalPageShell
      eyebrow="Rechtliches"
      title="Impressum"
      lead="Angaben gemäß § 5 Digitale-Dienste-Gesetz (DDG)."
    >
      {!isLegalContactConfigured && <LegalConfigurationNotice />}

      <LegalSection title="Anbieter">
        <address>
          {legalContact.name}
          <br />
          {legalContact.street}
          <br />
          {legalContact.cityLine}
          <br />
          {legalContact.country}
        </address>
      </LegalSection>

      <LegalSection title="Kontakt">
        <p>
          E-Mail: <ObfuscatedEmail email={legalContact.email} />
        </p>
      </LegalSection>

      <LegalSection title="Hinweis zum Angebot">
        <p>
          Modulio ist ein unabhängiges, nicht offizielles Studienberatungswerkzeug. Das Angebot
          ist nicht mit der Freien Universität Berlin verbunden und ersetzt keine verbindliche
          Auskunft der Universität oder des zuständigen Prüfungsbüros. Antworten werden von einem
          KI-Sprachmodell erzeugt und können fehlerhaft sein.
        </p>
      </LegalSection>
    </LegalPageShell>
  );
}
