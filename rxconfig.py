import reflex as rx
from reflex_components_radix.plugin import RadixThemesPlugin

config = rx.Config(
    app_name="hub_vix",
    telemetry_enabled=False,
    plugins=[
        RadixThemesPlugin(
            theme=rx.theme(
                appearance="dark",
                accent_color="indigo",
                gray_color="slate",
                radius="large",
            )
        )
    ],
)
