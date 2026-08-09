# Security

Security fixes land on `main`. This project is source-first (users build from the repo); there is no separate notarized binary release channel.

The app requests **Microphone** and **Accessibility** so it can record audio and paste text into other apps. Treat those permissions as high-impact when reviewing changes.
