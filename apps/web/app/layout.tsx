import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VTU Report Studio — Format your project report",
  description:
    "Create, format, validate and export your VTU engineering project report.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
