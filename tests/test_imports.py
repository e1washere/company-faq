def test_pinecone_demo_imports():
    import modules.m7_vector_swap.pinecone_demo as mod
    assert hasattr(mod, "main") 