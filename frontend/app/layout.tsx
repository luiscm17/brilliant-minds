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
              <div className="orb left-[-6rem] top-[-2rem] h-48 w-48 bg-[rgba(238,119,51,0.34)]" />
              <div className="orb left-[8%] top-12 h-20 w-20 bg-[rgba(0,68,136,0.22)]" />
              <div className="orb right-[-3rem] top-24 h-40 w-40 bg-[rgba(0,68,136,0.18)]" />
              <div className="orb bottom-[-1rem] left-[16%] h-40 w-40 bg-[rgba(17,119,51,0.18)]" />
              <div className="orb bottom-16 right-[-2rem] h-28 w-28 bg-[rgba(238,119,51,0.28)]" />
              <div className="challenge-ribbon left-[-4rem] top-[6.25rem] w-[28rem] rotate-[-10deg]" />
              <div className="challenge-ribbon silver right-[-5rem] bottom-[7rem] w-[24rem] rotate-[18deg]" />
              <div className="challenge-ribbon left-[24%] bottom-[2.5rem] w-[18rem] rotate-[8deg]" />
              <AppChrome>{children}</AppChrome>
            </div>
          </AccessibilityWrapper>
        </UserProvider>
      </body>
    </html>
  );
}
