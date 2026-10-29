# registry_synchronizer.py

class RegistrySynchronizer:

    def sync(
        self,
        metadata_registry,
        discovered_components
    ):

        count = 0

        for component in (
            discovered_components
        ):

            metadata_registry.register(
                component
            )

            count += 1

        return count