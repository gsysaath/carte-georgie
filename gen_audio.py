#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère l'audio géorgien des pages phrases.html et glossaire.html, hors-ligne,
avec eSpeak NG (voix synthétique libre) -> audio/ka/<n>.m4a, et écrit audio-ka.js
(window.KAUDIO : texte géorgien -> fichier audio).

    brew install espeak-ng       # une fois
    python3 gen_audio.py

afconvert (fourni par macOS) compresse le WAV en AAC/m4a (léger, lu par tous les
navigateurs). Relancer après avoir ajouté/édité des phrases.
"""
import html
import json
import os
import re
import subprocess

ICI = os.path.dirname(os.path.abspath(__file__))
PAGES = ["phrases.html", "glossaire.html"]
DEST = os.path.join(ICI, "audio", "ka")
VOICE, SPEED = "ka", "140"   # mots/min un peu ralentis pour la clarté

def collect():
    seen, texts = set(), []
    for p in PAGES:
        s = open(os.path.join(ICI, p), encoding="utf-8").read()
        for m in re.findall(r'data-ka="([^"]+)"', s):
            t = html.unescape(m).strip()
            if t and t not in seen:
                seen.add(t)
                texts.append(t)
    return texts

def main():
    os.makedirs(DEST, exist_ok=True)
    texts = collect()
    mapping, wav = {}, "/tmp/_ka_tts.wav"
    for i, t in enumerate(texts, 1):
        out = os.path.join(DEST, "%d.m4a" % i)
        with open(wav, "wb") as fh:
            subprocess.run(["espeak-ng", "-v", VOICE, "-s", SPEED, t, "--stdout"],
                           stdout=fh, check=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "64000", wav, out],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        mapping[t] = "audio/ka/%d.m4a" % i
    with open(os.path.join(ICI, "audio-ka.js"), "w", encoding="utf-8") as fh:
        fh.write("/* Audio géorgien généré hors-ligne par eSpeak NG (voix synthétique libre). */\n")
        fh.write("/* Régénérer : python3 gen_audio.py */\n")
        fh.write("window.KAUDIO = " + json.dumps(mapping, ensure_ascii=False) + ";\n")
    kb = sum(os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST)) / 1024
    print("Généré : %d clips (%.0f Ko au total) + audio-ka.js" % (len(mapping), kb))

if __name__ == "__main__":
    main()
