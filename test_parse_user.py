import sys
from biovia_pipeline.protocol_migration_engine import analyze_protocol_xml

def test():
    with open('test_user_full.xml', 'r') as f:
        content = f.read()
    res = analyze_protocol_xml(content)
    print("Total nodes:", res.total_nodes)
    print("Blue count:", res.blue_count)
    print("Green count:", res.green_count)
    print("Matched count:", res.matched_count)
    print("Missing count:", res.missing_count)
    print("Coverage:", res.coverage_percentage)
    for n in res.nodes:
        print(f"[{n.role.value}] ID={n.local_id} | Name={n.visual_name} | Core={n.core_name} | Status={n.status.value}")

if __name__ == '__main__':
    test()
