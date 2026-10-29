# missing_component_registry_updater.py

class MissingComponentRegistryUpdater:

    def update(
        self,
        registry,
        generated_component
    ):

        registry.register(

            generated_component
        )