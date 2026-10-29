```python
import os
import logging
from datetime import datetime

# It is assumed that the Pipeline Pilot specific imports (ComponentBase, InputPort, OutputPort, Parameter, DataType, ComponentError)
# are available in the execution environment.
# For local development or testing outside of a Pipeline Pilot installation,
# you might need to mock these classes. A basic mocking setup is provided below
# for demonstrative purposes, allowing the code to be syntactically valid and runnable
# for testing component logic. In a true Pipeline Pilot environment, these mocks
# would not be needed.

try:
    from accord.legato.component_base import ComponentBase
    from accord.legato.ports import InputPort, OutputPort, Parameter
    from accord.legato.types import DataType
    from accord.legato.exceptions import ComponentError
except ImportError:
    # --- Mocks for local development/testing outside Pipeline Pilot ---
    class ComponentBase:
        """
        A mock base class for Pipeline Pilot components for local testing.
        """
        def __init__(self, logger=None):
            self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
            # Initialize internal storage for mock ports/parameters
            self._input_ports = {}
            self._output_ports = {}
            self._parameters = {}

        def configure(self):
            """Mock configure method."""
            self.logger.info("Mock ComponentBase.configure called.")
            # In a real component, this would be defined by the framework.
            # For testing, we might manually set up ports/parameters if needed.

        def execute(self):
            """Mock execute method."""
            self.logger.info("Mock ComponentBase.execute called.")
            raise NotImplementedError("Subclasses should implement this!")

        def define_ports(self, inputs, outputs):
            """Mock method to define input and output ports."""
            for port_info in inputs:
                self._input_ports[port_info.name] = MockInputPort(port_info.name, self.logger)
            for port_info in outputs:
                self._output_ports[port_info.name] = MockOutputPort(port_info.name, self.logger)
            self.logger.debug(f"Mock ports defined: Inputs={list(self._input_ports.keys())}, Outputs={list(self._output_ports.keys())}")

        def define_parameters(self, parameters):
            """Mock method to define component parameters."""
            for param_info in parameters:
                mock_param = MockParameter(param_info.name, param_info.default_value)
                self._parameters[param_info.name] = mock_param
                self.logger.debug(f"Mock parameter '{param_info.name}' defined with default '{param_info.default_value}'")

        def get_input_port(self, name):
            """Mock method to get an input port by name."""
            return self._input_ports.get(name)

        def get_output_port(self, name):
            """Mock method to get an output port by name."""
            return self._output_ports.get(name)

        def get_parameter(self, name):
            """Mock method to get a parameter by name."""
            return self._parameters.get(name)

    class InputPort:
        """Mock InputPort class."""
        def __init__(self, name, data_type, description):
            self.name = name
            self.data_type = data_type
            self.description = description

    class OutputPort:
        """Mock OutputPort class."""
        def __init__(self, name, data_type, description):
            self.name = name
            self.data_type = data_type
            self.description = description

    class Parameter:
        """Mock Parameter class."""
        def __init__(self, name, data_type, default_value, description):
            self.name = name
            self.data_type = data_type
            self.default_value = default_value
            self.description = description

    class DataType:
        """Mock DataType class."""
        STRING = "string"
        BOOLEAN = "boolean"
        INTEGER = "integer" # Added for completeness if needed elsewhere

    class ComponentError(Exception):
        """Mock ComponentError class."""
        pass

    # Concrete mock port and parameter implementations for testing
    class MockInputPort:
        def __init__(self, name, logger):
            self.name = name
            self.logger = logger
            self._data = []
            self._index = 0

        def receive(self):
            """Simulate receiving data from an input stream."""
            if self._index < len(self._data):
                record = self._data[self._index]
                self._index += 1
                self.logger.debug(f"MockInputPort '{self.name}' received: {record}")
                return record
            self.logger.debug(f"MockInputPort '{self.name}' end of stream.")
            return None # Simulate end of stream

        def _set_test_data(self, data_list):
            """Method to inject test data into the mock input port."""
            self._data = list(data_list)
            self._index = 0
            self.logger.debug(f"MockInputPort '{self.name}' test data set: {data_list}")

    class MockOutputPort:
        def __init__(self, name, logger):
            self.name = name
            self.logger = logger
            self._data = []

        def send(self, data):
            """Simulate sending data to an output stream."""
            self.logger.debug(f"MockOutputPort '{self.name}' sent: {data}")
            self._data.append(data) # Store sent data for inspection in tests

        @property
        def data(self):
            """Allows inspection of data sent through the mock output port."""
            return self._data

    class MockParameter:
        def __init__(self, name, default_value):
            self.name = name
            self._value = default_value

        def get_value(self):
            """Returns the current value of the parameter."""
            return self._value

        def _set_test_value(self, value):
            """Method to set a test value for the parameter."""
            self._value = value

    # Configure logging for mock environment
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # --- End of Mocks ---


# Define component metadata required by Pipeline Pilot
COMPONENT_METADATA = {
    "name": "Delete File",
    "description": "Deletes a specified file from the file system. It can optionally halt processing "
                   "on error or emit an error message to a dedicated output port.",
    "component_type": "Utility",
    "category": "File Operations",
    "icon": "delete_file_icon.svg",  # Placeholder icon name
    "inputs": [
        InputPort(
            name="file_path",
            data_type=DataType.STRING,
            description="The full path to the file to be deleted."
        )
    ],
    "outputs": [
        OutputPort(
            name="deleted_file_path",
            data_type=DataType.STRING,
            description="The path of the file that was successfully deleted."
        ),
        OutputPort(
            name="error_message",
            data_type=DataType.STRING,
            description="An error message if the file deletion failed. This port will be empty "
                        "if the operation was successful. If 'Fail on error' is checked and an error occurs, "
                        "the protocol will stop, and this port will not receive an error message."
        )
    ],
    "parameters": [
        Parameter(
            name="fail_on_error",
            data_type=DataType.BOOLEAN,
            default_value=True,
            description="If checked, the component will raise an exception and stop the protocol "
                        "if the file cannot be deleted. If unchecked, it will emit an error "
                        "message to the 'error_message' port and continue processing."
        )
    ]
}


class DeleteFile(ComponentBase):
    """
    A Pipeline Pilot component that deletes files from the file system.
    It takes file paths as input and provides outputs for successfully
    deleted paths or error messages.
    """

    def configure(self):
        """
        Configures the component by defining its input and output ports
        and parameters based on COMPONENT_METADATA.
        """
        self.logger.info("Configuring Delete File component...")
        self.define_ports(COMPONENT_METADATA["inputs"], COMPONENT_METADATA["outputs"])
        self.define_parameters(COMPONENT_METADATA["parameters"])
        self.logger.info("Delete File component configured.")

    def execute(self):
        """
        Executes the file deletion logic for each incoming file path record.
        It processes records from the 'file_path' input port, attempts to
        delete the specified file, and routes the result to either the
        'deleted_file_path' or 'error_message' output port.
        """
        self.logger.info("Executing Delete File component...")

        input_port = self.get_input_port("file_path")
        deleted_output_port = self.get_output_port("deleted_file_path")
        error_output_port = self.get_output_port("error_message")
        fail_on_error = self.get_parameter("fail_on_error").get_value()

        # Process records until the input stream is exhausted
        record = input_port.receive()
        while record is not None:
            file_path_to_delete = record
            self.logger.info(f"Attempting to delete file: '{file_path_to_delete}'")

            try:
                # Check if the file exists before attempting to delete
                if not os.path.exists(file_path_to_delete):
                    error_msg = f"File not found: '{file_path_to_delete}'"
                    self.logger.warning(error_msg)
                    if fail_on_error:
                        raise ComponentError(error_msg)
                    error_output_port.send(error_msg)
                    # Move to the next record if not failing on error
                    record = input_port.receive()
                    continue

                # Attempt to delete the file
                os.remove(file_path_to_delete)
                self.logger.info(f"Successfully deleted file: '{file_path_to_delete}'")
                deleted_output_port.send(file_path_to_delete)

            except OSError as e:
                # Catch specific OS errors (e.g., permission denied, file in use)
                error_msg = f"Failed to delete file '{file_path_to_delete}': {e}"
                self.logger.error(error_msg, exc_info=True)
                if fail_on_error:
                    raise ComponentError(error_msg)
                error_output_port.send(error_msg)
            except Exception as e:
                # Catch any other unexpected errors during deletion
                error_msg = f"An unexpected error occurred while deleting '{file_path_to_delete}': {e}"
                self.logger.critical(error_msg, exc_info=True)
                if fail_on_error:
                    raise ComponentError(error_msg)
                error_output_port.send(error_msg)

            # Receive the next record from the input stream
            record = input_port.receive()

        self.logger.info("Delete File component execution finished.")


# --- Example of local testing using the mocks ---
if __name__ == "__main__":
    print("--- Starting Local Test for Delete File Component ---")

    # Create dummy files for testing
    test_file_success = "temp_delete_test_success.txt"
    test_file_permission_denied = "temp_delete_test_permission_denied.txt"
    test_file_non_existent = "non_existent_file_for_test.txt"

    # Setup success file
    with open(test_file_success, "w") as f:
        f.write("This file should be deleted successfully.")

    # Setup permission denied file (may require specific OS privileges to truly deny access)
    try:
        with open(test_file_permission_denied, "w") as f:
            f.write("This file should cause a permission error.")
        # Attempt to remove all permissions for testing
        os.chmod(test_file_permission_denied, 0o000)
    except OSError as e:
        print(f"WARNING: Could not set restricted permissions for '{test_file_permission_denied}': {e}. "
              "Permission denied test case might not fully demonstrate behavior.")
        test_file_permission_denied = None # Disable this test if setup fails

    # --- Test Case 1: Successful deletion with fail_on_error=True (default) ---
    print("\n--- Test Case 1: Successful Deletion ---")
    component1 = DeleteFile()
    component1.configure()
    component1.get_parameter("fail_on_error")._set_test_value(True)
    component1.get_input_port("file_path")._set_test_data([test_file_success])
    component1.execute()
    assert not os.path.exists(test_file_success), "Test 1 Failed: File was not deleted."
    assert component1.get_output_port("deleted_file_path").data == [test_file_success], "Test 1 Failed: Output mismatch."
    assert not component1.get_output_port("error_message").data, "Test 1 Failed: Error message unexpectedly present."
    print("Test Case 1 Passed: File deleted successfully.")

    # --- Test Case 2: File not found with fail_on_error=True (should raise ComponentError) ---
    print("\n--- Test Case 2: File Not Found (Fail on Error) ---")
    component2 = DeleteFile()
    component2.configure()
    component2.get_parameter("fail_on_error")._set_test_value(True)
    component2.get_input_port("file_path")._set_test_data([test_file_non_existent])
    try:
        component2.execute()
        assert False, "Test 2 Failed: Expected ComponentError was not raised."
    except ComponentError as e:
        print(f"Test 2 Passed: Caught expected error: '{e}'")
        assert "File not found" in str(e), "Test 2 Failed: Error message content mismatch."
    assert not component2.get_output_port("deleted_file_path").data, "Test 2 Failed: Output mismatch."
    assert not component2.get_output_port("error_message").data, "Test 2 Failed: Error message unexpectedly present."

    # --- Test Case 3: File not found with fail_on_error=False (should emit error message) ---
    print("\n--- Test Case 3: File Not Found (No Fail on Error) ---")
    component3 = DeleteFile()
    component3.configure()
    component3.get_parameter("fail_on_error")._set_test_value(False)
    component3.get_input_port("file_path")._set_test_data([test_file_non_existent])
    component3.execute()
    assert not os.path.exists(test_file_non_existent), "Test 3 Failed: Non-existent file should remain non-existent."
    assert not component3.get_output_port("deleted_file_path").data, "Test 3 Failed: Output mismatch."
    assert "File not found" in component3.get_output_port("error_message").data[0], "Test 3 Failed: Error message content mismatch."
    print(f"Test 3 Passed: Error message emitted: '{component3.get_output_port('error_message').data[0]}'")

    # --- Test Case 4: Permission Denied with fail_on_error=True (if setup allows) ---
    if test_file_permission_denied and os.path.exists(test_file_permission_denied):
        print("\n--- Test Case 4: Permission Denied (Fail on Error) ---")
        component4 = DeleteFile()
        component4.configure()
        component4.get_parameter("fail_on_error")._set_test_value(True)
        component4.get_input_port("file_path")._set_test_data([test_file_permission_denied])
        try:
            component4.execute()
            assert False, "Test 4 Failed: Expected ComponentError was not raised for permission denied."
        except ComponentError as e:
            print(f"Test 4 Passed: Caught expected error: '{e}'")
            # Error message can vary by OS (e.g., "Permission denied" vs "Access is denied")
            assert "permission denied" in str(e).lower() or "access is denied" in str(e).lower(), \
                "Test 4 Failed: Error message content mismatch for permission denied."
        assert not component4.get_output_port("deleted_file_path").data, "Test 4 Failed: Output mismatch."
        assert not component4.get_output_port("error_message").data, "Test 4 Failed: Error message unexpectedly present."
    else:
        print("\n--- Test Case 4: Permission Denied test skipped due to setup limitations. ---")

    # --- Cleanup ---
    print("\n--- Cleaning up test files ---")
    for fname in [test_file_success, test_file_non_existent]: # test_file_success should be gone
        if os.path.exists(fname):
            try:
                os.remove(fname)
                print(f"Cleaned up '{fname}'.")
            except OSError as e:
                print(f"Error cleaning up '{fname}': {e}")
    if test_file_permission_denied and os.path.exists(test_file_permission_denied):
        try:
            os.chmod(test_file_permission_denied, 0o777) # Restore permissions first
            os.remove(test_file_permission_denied)
            print(f"Cleaned up '{test_file_permission_denied}'.")
        except OSError as e:
            print(f"Error cleaning up '{test_file_permission_denied}': {e}")

    print("\n--- All local tests finished ---")
```