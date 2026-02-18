import "./globals.css";

export const metadata = {
    title: "Strategic Grid // Command Center",
    description: "Multi-Agent Sales Intelligence Dashboard",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
