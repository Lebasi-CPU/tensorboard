import os
import json
import pytest
import asyncio
from financial_models import settings
from main import NexusSymbiote

def test_settings_load():
    assert settings.MAYA_RESONANCE_PHASE == 4
    assert settings.REGION in ["CHINA", "RUSSIA", "JAPAN", "EUROPE", "WEST"]

def test_symbiote_initialization():
    symbiote = NexusSymbiote()
    assert "VANGUARD-NEXUS" in symbiote.node_id

def test_extract_neutrino_data():
    symbiote = NexusSymbiote()
    intel = symbiote.extract_neutrino_data("http://test.com")
    assert "raw_intel" in intel
    assert "timestamp" in intel

@pytest.mark.asyncio
async def test_cognitive_fusion_synthesis():
    symbiote = NexusSymbiote()
    intel = {"timestamp": "2026-02-27", "raw_intel": "test"}
    synthesis = await symbiote.cognitive_fusion_synthesis(intel)
    assert "SÍNTESIS VANGUARDIA" in synthesis

def test_maya_mesh_sync():
    symbiote = NexusSymbiote()
    status = symbiote.maya_mesh_sync("test report")
    assert status == "SYNC_COMPLETE_STABLE"
