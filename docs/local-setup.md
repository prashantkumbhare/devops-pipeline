# Local Windows setup

Use installed VS Code, Git and Docker Desktop with Linux containers through WSL 2.

## Initial findings — 3 October 2026

- Git: 2.49.0.windows.1.
- VS Code: 1.139.1, x64.
- WSL reports that it is not installed.
- Docker is not on the current terminal PATH. A per-user DockerDesktop directory exists, but access to inspect its executable was denied. The installation and engine are not verified.
- Windows version reported: 10.0.26200.0. RAM and firmware virtualization queries were denied; confirm those locally if Docker reports a requirement problem.

## Prepare the runtime

1. Open PowerShell as Administrator and run `wsl --install`. Follow prompts and restart if required.
2. Open existing Docker Desktop if available. Otherwise install from the official Docker documentation. Choose the WSL 2 backend and Linux containers. Review the subscription agreement yourself.
3. Wait until Docker Desktop reports that its engine is running.
4. Open a fresh VS Code terminal in this repository, then run:

```powershell
.\scripts\check-environment.cmd --smoke-test
```

The smoke test downloads the official `hello-world` image, runs a disposable container and removes that container. The cached image remains available.

Do not close issue D01 until the Docker engine, Compose version and smoke test have succeeded.

## What you should understand

- An image is a packaged filesystem and application configuration; a container is a running instance.
- Docker Desktop uses a Linux runtime for these Linux containers. WSL 2 supplies that Linux environment on Windows.
- Docker CLI availability and Docker engine availability are separate checks.
- Docker Compose describes a set of services, networks and volumes. We add the trading API and database next.

## Sources

- [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Docker Desktop Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/)

## Git download troubleshooting

The initial clone failed with a Windows Schannel credential error. A one-command override to the OpenSSL backend succeeded without disabling certificate checks:

```powershell
git -c http.sslBackend=openssl clone https://github.com/prashantkumbhare/devops-pipeline.git
```

No global Git settings were changed.

