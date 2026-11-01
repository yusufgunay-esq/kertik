#!/usr/bin/env python3
"""Kertik'i tek komutla derler: python3 derle.py

Şablon APK + güncel index.html -> imzalı APK.
Parolayı KERTIK_PAROLA ortam değişkeninden ya da yanındaki parola.txt'den okur.
"""
import os, sys, subprocess

BURA = os.path.dirname(os.path.abspath(__file__))
SABLON = os.environ.get("KERTIK_SABLON", os.path.join(BURA, "sablon.apk"))
HTML = os.environ.get("KERTIK_HTML", os.path.join(BURA, "..", "www", "index.html"))
CIKTI = os.environ.get("KERTIK_CIKTI", os.path.join(BURA, "..", "Kertik.apk"))
ANAHTAR = os.path.join(BURA, "kertik-imza.p12")

parola = os.environ.get("KERTIK_PAROLA")
if not parola:
    yol = os.path.join(BURA, "parola.txt")
    if os.path.exists(yol):
        parola = open(yol).read().strip()
if not parola:
    sys.exit("Parola yok: KERTIK_PAROLA ortam değişkenini ver ya da imza/parola.txt yaz.")

subprocess.run([sys.executable, os.path.join(BURA, "apkbuild.py"),
                SABLON, HTML, CIKTI, ANAHTAR, parola], check=True)

subprocess.run([sys.executable, "-m", "apksigtool", "verify", CIKTI], check=True)
subprocess.run(["jarsigner", "-verify", CIKTI], check=True)
print("hazır:", CIKTI)
