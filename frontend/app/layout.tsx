import "./globals.css";
import { UserProvider } from "../context/UserContext";
import AccessibilityWrapper from "../components/AccessibilityWrapper";
import AppChrome from "../components/AppChrome";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        <UserProvider>
          <AccessibilityWrapper>
            <div className="relative min-h-screen overflow-hidden px-4 py-8 md:px-8 md:py-10">
              <div className="orb left-[-6rem] top-8 h-40 w-40 bg-[rgba(226,184,95,0.55)]" />
              <div className="orb right-[-4rem] top-20 h-36 w-36 bg-[rgba(13,122,116,0.25)]" />
              <div className="orb bottom-0 left-[20%] h-32 w-32 bg-[rgba(222,123,89,0.28)]" />
              <AppChrome>{children}</AppChrome>
            </div>
          </AccessibilityWrapper>
        </UserProvider>
      </body>
    </html>
  );
}
