import hashlib
import json
from datetime import datetime
from backend.generator.data_factory import DataFactory

class ReproducibilityVerifier:
    @staticmethod
    def verify(seed=20261022, scale="starter"):
        """
        Runs generation twice with identical seed and configuration,
        computes SHA256 checksums across all tables, row counts,
        and primary ID sequences.
        """
        # Run 1
        factory_1 = DataFactory(seed=seed)
        data_1 = factory_1.generate_all(scale=scale)

        # Run 2
        factory_2 = DataFactory(seed=seed)
        data_2 = factory_2.generate_all(scale=scale)

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "fixed_seed": seed,
            "scale": scale,
            "is_reproducible": True,
            "tables_compared": list(data_1.keys()),
            "table_reports": {}
        }

        for table_name in data_1.keys():
            recs_1 = data_1[table_name]
            recs_2 = data_2[table_name]

            # 1. Compare row counts
            count_1 = len(recs_1)
            count_2 = len(recs_2)
            counts_match = (count_1 == count_2)

            # 2. Compare IDs
            ids_1 = [str(r.get("id")) for r in recs_1]
            ids_2 = [str(r.get("id")) for r in recs_2]
            ids_match = (ids_1 == ids_2)

            # 3. Compute JSON and CSV representation hashes
            json_str_1 = json.dumps(recs_1, sort_keys=True, default=str)
            json_str_2 = json.dumps(recs_2, sort_keys=True, default=str)
            hash_json_1 = hashlib.sha256(json_str_1.encode("utf-8")).hexdigest()
            hash_json_2 = hashlib.sha256(json_str_2.encode("utf-8")).hexdigest()
            json_match = (hash_json_1 == hash_json_2)

            # CSV line hash
            csv_lines_1 = [",".join(str(v) for v in r.values()) for r in recs_1]
            csv_lines_2 = [",".join(str(v) for v in r.values()) for r in recs_2]
            hash_csv_1 = hashlib.sha256("\n".join(csv_lines_1).encode("utf-8")).hexdigest()
            hash_csv_2 = hashlib.sha256("\n".join(csv_lines_2).encode("utf-8")).hexdigest()
            csv_match = (hash_csv_1 == hash_csv_2)

            table_status = counts_match and ids_match and json_match and csv_match
            if not table_status:
                report["is_reproducible"] = False

            report["table_reports"][table_name] = {
                "row_count_run_1": count_1,
                "row_count_run_2": count_2,
                "row_counts_identical": counts_match,
                "ids_identical": ids_match,
                "json_checksum_run_1": hash_json_1,
                "json_checksum_run_2": hash_json_2,
                "json_checksums_identical": json_match,
                "csv_checksum_run_1": hash_csv_1,
                "csv_checksum_run_2": hash_csv_2,
                "csv_checksums_identical": csv_match,
                "status": "IDENTICAL" if table_status else "MISMATCH"
            }

        return report
