from backend.generator.reproducibility import ReproducibilityVerifier

def test_fixed_seed_reproducibility():
    report = ReproducibilityVerifier.verify(seed=20261022, scale="starter")
    assert report["is_reproducible"] is True
    assert report["fixed_seed"] == 20261022

    # Check that every table is IDENTICAL
    for table_name, rep in report["table_reports"].items():
        assert rep["status"] == "IDENTICAL", f"Table {table_name} was not identical across runs"
        assert rep["row_counts_identical"] is True
        assert rep["ids_identical"] is True
        assert rep["json_checksums_identical"] is True
        assert rep["csv_checksums_identical"] is True
