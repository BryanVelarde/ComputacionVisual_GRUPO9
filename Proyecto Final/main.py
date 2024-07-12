import flet as ft 
from cameraCalibrator import run_main
from scanner import scann_main

def main(page: ft.Page):
    page.title = "Scanner 3D"
    page.theme_mode = ft.ThemeMode.LIGHT

    def runCameraCalibrator(e):
        run_main()

    def runScanner(e):
        scann_main()

    buttonRunCameraCalibrator = ft.ElevatedButton(text="Calibrar Camara", on_click=runCameraCalibrator)
    buttonScann = ft.ElevatedButton(text="Comenzar a escanear", on_click=runScanner)

    page.add(
        buttonRunCameraCalibrator,
        buttonScann
    )

ft.app(target=main)
