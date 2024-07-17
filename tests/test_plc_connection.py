import snap7
import pytest
from unittest.mock import patch, MagicMock

#from snap7.snap7exceptions import Snap7Exception
#from snap7.snap7types import S7CpuInfo
     
@pytest.fixture
def mock_client():
    with patch('snap7.client.Client') as MockClient:
        mock_client = MockClient.return_value
        yield mock_client
        
def test_connect(mock_client):
    # simulate the connection is successful
    mock_client.get_connected.side_effect = [True, False]

    # Create a client and connect to the PLC
    client = snap7.client.Client()
    client.connect('192.168.0.100', 0, 1)
    assert client.get_connected() == True
    client.disconnect()
    assert client.get_connected() == False        