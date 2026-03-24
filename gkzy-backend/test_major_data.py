from app import create_app, db
from app.models.major import Major
from app.models.major_employment import MajorEmployment

app = create_app()

with app.app_context():
    # 检查专业表数据
    print("=" * 50)
    print("检查专业表数据...")
    majors = Major.query.limit(5).all()
    print(f"专业表总记录数：{Major.query.count()}")
    for major in majors:
        print(f"  - ID: {major.id}, 名称：{major.name}, 描述：{major.description[:50] if major.description else 'None'}")
    
    print("\n" + "=" * 50)
    print("检查就业数据表数据...")
    employments = MajorEmployment.query.limit(5).all()
    print(f"就业数据表总记录数：{MajorEmployment.query.count()}")
    for emp in employments:
        print(f"  - ID: {emp.id}, 专业 ID: {emp.major_id}, 平均薪资：{emp.avg_salary}, 年份：{emp.year}")
    
    print("\n" + "=" * 50)
    print("检查关联查询...")
    from sqlalchemy import desc
    query = db.session.query(
        Major.id,
        Major.name,
        Major.description,
        MajorEmployment.avg_salary,
        MajorEmployment.year
    ).join(
        MajorEmployment, Major.id == MajorEmployment.major_id
    ).order_by(
        desc(MajorEmployment.avg_salary)
    ).limit(6)
    
    results = query.all()
    print(f"关联查询结果数量：{len(results)}")
    for row in results:
        print(f"  - ID: {row.id}, 名称：{row.name}, 薪资：{row.avg_salary}")
    
    print("\n" + "=" * 50)
