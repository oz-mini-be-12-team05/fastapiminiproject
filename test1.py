from graphviz import Digraph

# ERD 객체 생성
erd = Digraph('ERD_with_Types', format='png')
erd.attr(rankdir='LR', fontsize='10')

# 테이블 구조 정의
tables = {
    "users": [
        "id: SERIAL (PK)",
        "email: VARCHAR(255)",
        "password: VARCHAR(255)",
        "nickname: VARCHAR(100)",
        "name: VARCHAR(100)",
        "phone_number: VARCHAR(20)",
        "last_login: TIMESTAMP",
        "is_staff: BOOLEAN",
        "is_superuser: BOOLEAN",
        "is_active: BOOLEAN",
        "created_at: TIMESTAMP",
        "updated_at: TIMESTAMP"
    ],
    "diaries": [
        "id: SERIAL (PK)",
        "user_id: INTEGER (FK)",
        "title: VARCHAR(255)",
        "content: TEXT",
        "ai_summary: TEXT",
        "main_emotion: VARCHAR(50)",
        "created_at: TIMESTAMP",
        "updated_at: TIMESTAMP"
    ],
    "tags": [
        "id: SERIAL (PK)",
        "name: VARCHAR(50)"
    ],
    "diary_tags": [
        "id: SERIAL (PK)",
        "diary_id: INTEGER (FK)",
        "tag_id: INTEGER (FK)"
    ],
    "emotion_keywords": [
        "id: SERIAL (PK)",
        "keyword: VARCHAR(50)",
        "emotion_type: VARCHAR(50)"
    ],
    "diary_emotion_keywords": [
        "id: SERIAL (PK)",
        "diary_id: INTEGER (FK)",
        "emotion_keyword_id: INTEGER (FK)"
    ],
    "emotion_stats": [
        "id: SERIAL (PK)",
        "user_id: INTEGER (FK)",
        "period: VARCHAR(50)",
        "emotion_type: VARCHAR(50)",
        "emotion_count: INTEGER",
        "start_date: DATE",
        "end_date: DATE"
    ],
    "alert_logs": [
        "id: SERIAL (PK)",
        "user_id: INTEGER (FK)",
        "message: TEXT",
        "created_at: TIMESTAMP"
    ]
}

# 테이블 노드 추가
for table, fields in tables.items():
    label = f"<<TABLE BORDER='1' CELLBORDER='0' CELLSPACING='0'>"
    label += f"<TR><TD BGCOLOR='lightblue'><B>{table}</B></TD></TR>"
    for field in fields:
        label += f"<TR><TD ALIGN='LEFT'>{field}</TD></TR>"
    label += "</TABLE>>"
    erd.node(table, label=label, shape='plaintext')

# 관계(FK) 정의
relations = [
    ("diaries", "users"),
    ("diary_tags", "diaries"),
    ("diary_tags", "tags"),
    ("diary_emotion_keywords", "diaries"),
    ("diary_emotion_keywords", "emotion_keywords"),
    ("emotion_stats", "users"),
    ("alert_logs", "users"),
]

# 관계선 추가
for src, dst in relations:
    erd.edge(src, dst, arrowhead='vee', arrowsize='0.7')

# 이미지 렌더링
erd.render('erd_with_types', cleanup=True)
