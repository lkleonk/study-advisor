import type { Metadata } from "next";

import {
  LegalConfigurationNotice,
  LegalPageShell,
  LegalSection,
} from "@/components/LegalPageShell";
import { ObfuscatedEmail } from "@/components/ObfuscatedEmail";
import { isLegalContactConfigured, legalContact } from "@/config/legalContact";

export const metadata: Metadata = {
  title: "Datenschutzerklärung | Modulio",
  description: "Informationen zur Verarbeitung personenbezogener Daten durch Modulio.",
};

export default function DatenschutzPage() {
  return (
    <LegalPageShell
      eyebrow="Datenschutz"
      title="Datenschutzerklärung"
      lead="Diese Datenschutzerklärung erläutert die Verarbeitung personenbezogener Daten bei der Nutzung von Modulio. Stand: 8. Oktober 2026."
    >
      {!isLegalContactConfigured && <LegalConfigurationNotice />}

      <LegalSection title="1. Verantwortlicher">
        <address>
          {legalContact.name}
          <br />
          {legalContact.street}
          <br />
          {legalContact.cityLine}
          <br />
          {legalContact.country}
        </address>
        <p>
          E-Mail: <ObfuscatedEmail email={legalContact.email} />
        </p>
      </LegalSection>

      <LegalSection title="2. Hosting und technische Zugriffsdaten">
        <p>
          Beim Aufruf der Website verarbeiten der Webserver und der Hosting-Anbieter technisch
          notwendige Zugriffsdaten. Dazu können insbesondere IP-Adresse, Zeitpunkt des Zugriffs,
          angeforderte Ressource, Referrer, Browser- und Betriebssysteminformationen sowie
          Server-Logdaten gehören.
        </p>
        <p>
          Die Website wird als statische Seite über Microsoft Azure Storage bereitgestellt;
          der Backend-Dienst läuft in Microsoft Azure Container Apps. Beide werden im
          Azure-Rechenzentrum Schweiz Nord (Zürich) betrieben. Der Abruf der Website läuft
          zusätzlich über das Content-Delivery-Netzwerk von Cloudflare, das die Verbindung
          verschlüsselt und die Website vor Angriffen schützt. Anfragen an den Backend-Dienst,
          also Chatnachrichten und PDF-Uploads, werden direkt an Azure gesendet und laufen
          nicht über Cloudflare.
        </p>
        <p>
          Die Verarbeitung dient der sicheren und stabilen Bereitstellung des Angebots. Sie
          erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO. Protokolle des Backend-Dienstes
          werden in Azure Log Analytics 30 Tage lang gespeichert und danach automatisch
          gelöscht. Für die Protokolle von Cloudflare gelten dessen eigene Speicherfristen.
        </p>
      </LegalSection>

      <LegalSection title="3. Beratungsanfragen und LLM-Verarbeitung">
        <p>
          Wenn Sie eine Nachricht senden, verarbeitet der Backend-Dienst den Nachrichteninhalt,
          eine zufällig erzeugte Sitzungs-ID und die für die Antwort benötigten bisherigen
          Sitzungsdaten. Eingaben werden zur Beantwortung an den Sprachmodell-Dienst der
          AcademicCloud (siehe Abschnitt 8) übermittelt. Eine Anfrage kann mehrere
          Modellaufrufe auslösen.
        </p>
        <p>
          Die Verarbeitung ist erforderlich, um die ausdrücklich angeforderte Studienberatung
          bereitzustellen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Bitte übermitteln Sie
          keine Daten, die für die Beratung nicht erforderlich sind.
        </p>
      </LegalSection>

      <LegalSection title="4. Upload von Leistungsübersichten">
        <p>
          Der optionale PDF-Upload überträgt die Datei an den Backend-Dienst. Dort wird Text aus
          der PDF extrahiert und ungekürzt an den Sprachmodell-Dienst gesendet,
          um Module und Leistungspunkte zu erkennen. Bildbasierte oder unzureichend lesbare PDFs
          werden abgelehnt. Die maximale Dateigröße beträgt 15 MB.
        </p>
        <p>
          Anschließend werden nur der strukturierte Studienplan und das Ergebnis der
          regelbasierten Prüfung in der Sitzung weitergeführt. Die PDF-Datei und der daraus
          extrahierte Text werden nicht gespeichert.
        </p>
      </LegalSection>

      <LegalSection title="5. Sitzungs- und Browserdaten">
        <p>
          Der Backend-Dienst hält Sitzungsdaten im Arbeitsspeicher. Standardmäßig werden inaktive
          Sitzungen nach 48 Stunden bei der nächsten Bereinigungsgelegenheit entfernt; ein
          Neustart des Dienstes löscht den Arbeitsspeicher ebenfalls. Über „Reset conversation“
          kann die aktuelle Sitzung vorher gelöscht werden. Eine bereits laufende Anfrage wird
          zunächst abgeschlossen.
        </p>
        <p>
          Der Browser speichert die Sitzungs-ID, angezeigte Chatnachrichten und strukturierte
          Studienplandaten im <code>sessionStorage</code>. Darstellungs- und Dialogeinstellungen
          werden im <code>localStorage</code> gespeichert. Diese Daten verbleiben im verwendeten
          Browser, bis der jeweilige Browserspeicher endet oder zurückgesetzt wird.
        </p>
      </LegalSection>

      <LegalSection title="6. Nutzungslimit und IP-Adresse">
        <p>
          Zur Durchsetzung des täglichen Nutzungslimits führt der Backend-Dienst einen
          prozesslokalen Zähler je Client-IP-Adresse. Der Zähler wird um 00:00 Uhr UTC und bei
          einem Neustart des Backend-Prozesses zurückgesetzt. Die Verarbeitung dient dem Schutz
          des Dienstes vor Überlastung und Missbrauch und erfolgt auf Grundlage von Art. 6 Abs. 1
          lit. f DSGVO.
        </p>
      </LegalSection>

      <LegalSection title="7. Diagnosedaten">
        <p>
          Modulio zeichnet keine Gesprächsinhalte zu Diagnosezwecken auf. Chatnachrichten,
          Modellantworten und hochgeladene Dokumente werden nicht in Diagnose- oder
          Trace-Dateien gespeichert.
        </p>
      </LegalSection>

      <LegalSection title="8. Empfänger und Auftragsverarbeiter">
        <ul>
          <li>
            <strong>Microsoft Azure</strong> (Microsoft) für Hosting, Backend-Dienst und
            Protokollierung. Die Server stehen in der Schweiz (Azure-Region Schweiz Nord,
            Zürich). Für die Schweiz besteht ein Angemessenheitsbeschluss der EU-Kommission.
          </li>
          <li>
            <strong>Cloudflare</strong> (Cloudflare, Inc., USA) als Content-Delivery-Netzwerk für
            den Abruf der Website. Cloudflare ist unter dem EU-US Data Privacy Framework
            zertifiziert.
          </li>
          <li>
            <strong>AcademicCloud</strong> (Gesellschaft für wissenschaftliche Datenverarbeitung
            mbH Göttingen, GWDG) als Sprachmodell-Dienst für Chatnachrichten und
            PDF-Inhalte. Die Verarbeitung erfolgt in Deutschland.
          </li>
        </ul>
      </LegalSection>

      <LegalSection title="9. Cookies, Analytics und Tracking">
        <p>
          Modulio setzt nach aktuellem Stand keine eigenen Cookies ein und verwendet keine
          Analytics-, Werbe- oder Tracking-Dienste. Die oben beschriebenen Browser-Speicher
          dienen ausschließlich der Funktion und Darstellung des Angebots.
        </p>
      </LegalSection>

      <LegalSection title="10. Rechte betroffener Personen">
        <p>
          Im Rahmen der gesetzlichen Voraussetzungen bestehen insbesondere Rechte auf Auskunft,
          Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und
          Widerspruch. Außerdem besteht ein Beschwerderecht bei einer zuständigen
          Datenschutzaufsichtsbehörde.
        </p>
      </LegalSection>

      <LegalSection title="11. Aktualisierungen">
        <p>
          Wir passen diese Datenschutzerklärung an, wenn sich die beschriebenen Verarbeitungen
          ändern. Es gilt die jeweils auf dieser Seite veröffentlichte Fassung.
        </p>
      </LegalSection>
    </LegalPageShell>
  );
}
