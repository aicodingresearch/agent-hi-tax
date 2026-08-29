<!-- Remove this page and its README link when the repository is made public. -->

# Internal pilot notes

**English** | [中文](internal-pilot.zh-CN.md)

This page applies only to invited contributors while the repository is private.

## Before accepting the invitation

- Enable two-factor authentication (2FA) on your GitHub account first. The organization requires 2FA, so an account without it cannot join.
- In GitHub email settings, enable **Keep my email addresses private**. Use your GitHub noreply address for commits so your real email will not be exposed in Git history if the repository later becomes public:

  ```sh
  git config user.email "<id>+<login>@users.noreply.github.com"
  ```

## Contribution path

Invitees collaborate with **Read** access: fork the repository, clone your private fork, create a branch, and open a Pull Request. The fork remains private; GitHub automatically deletes it if you lose access to the private upstream repository.

For a first contribution, allow about **1 hour**, which is enough to complete one scenario. Once you know the process, a typical contribution can be completed in about **30 minutes**.

On Windows, run the verification scripts in a POSIX environment such as Git Bash or WSL. Collect the preflight equivalents in PowerShell (replace `<agent>`):

```powershell
Get-Command <agent> | Select-Object -ExpandProperty Source
<agent> --version
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture
(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
```

## Private contact

For privacy concerns or suspected leaks during the private pilot, contact the maintainer directly through the channel that carried your invitation. GitHub private vulnerability reporting is unavailable for a private repository; it will be enabled after the repository becomes public.
