using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Windows.Forms;

internal static class Setup
{
    [STAThread]
    private static int Main(string[] args)
    {
        bool extractOnly = args.Length == 2 && args[0] == "--extract";
        if (!extractOnly && MessageBox.Show(
            "Install Peeky 3 for your Windows account?\n\nSetup downloads the local AI and speech models if needed. Keep the installer open until it finishes.",
            "Peeky 3 Setup", MessageBoxButtons.OKCancel, MessageBoxIcon.Information) != DialogResult.OK)
            return 0;

        string staging = extractOnly ? Path.GetFullPath(args[1]) :
            Path.Combine(Path.GetTempPath(), "Peeky3Setup-" + Guid.NewGuid().ToString("N"));
        try
        {
            Directory.CreateDirectory(staging);
            using (Stream resource = Assembly.GetExecutingAssembly().GetManifestResourceStream("Payload"))
            using (ZipArchive archive = new ZipArchive(resource, ZipArchiveMode.Read))
                archive.ExtractToDirectory(staging);
            if (extractOnly)
                return 0;

            string powershell = Path.Combine(Environment.SystemDirectory, "WindowsPowerShell", "v1.0", "powershell.exe");
            ProcessStartInfo info = new ProcessStartInfo(powershell,
                "-NoProfile -ExecutionPolicy Bypass -File \"" + Path.Combine(staging, "Install.ps1") + "\"");
            info.WorkingDirectory = staging;
            info.UseShellExecute = false;
            using (Process script = Process.Start(info))
            {
                script.WaitForExit();
                if (script.ExitCode == 0)
                    MessageBox.Show("Installation complete. Open Peeky 3 from your desktop.",
                        "Peeky 3 Setup", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return script.ExitCode;
            }
        }
        catch (Exception error)
        {
            if (extractOnly)
                Console.Error.WriteLine(error);
            else
                MessageBox.Show(error.Message, "Peeky 3 Setup", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
        finally
        {
            if (!extractOnly)
            {
                try { Directory.Delete(staging, true); }
                catch (IOException) {}
                catch (UnauthorizedAccessException) {}
            }
        }
    }
}

