

# from flask import Blueprint, request, jsonify, render_template
# from sqlalchemy import text
# import pandas as pd
# #from application.backend.db_connect import get_database_engine
# from application.backend.engine import engine

# # Blueprint for Portfolio
# portfolio_bp = Blueprint('portfolio', __name__)
# #engine = get_database_engine()

# @portfolio_bp.route('/portfolio')
# def view_portfolio():
#     query = 'SELECT * FROM "portfolio" ORDER BY "seccode" ASC'
#     with engine.connect() as conn:
#         portfolio_df = pd.read_sql(query, conn)
#     return render_template('portfolio.html', portfolio=portfolio_df.to_dict('records'))

# @portfolio_bp.route('/add_to_portfolio', methods=['POST'])
# def add_to_portfolio():
#     sec_code = request.form.get('seccode')
#     if not sec_code:
#         return jsonify({"message": "seccode is required"}), 400
#     query = """SELECT COUNT(1) FROM portfolio WHERE "seccode" = :sec_code"""
#     try:
#         with engine.connect() as conn:
#             result = conn.execute(text(query), {"sec_code": sec_code})
#             count = result.scalar()
#             if count > 0:
#                 return jsonify({"message": f"Sec Code {sec_code} is already in the portfolio."}), 200
#             company_details = pd.read_sql(
#                 """
#                 SELECT n."seccode", n."companyname", n."fiscalyearend", n."quarter",
#                        n."growth_percentage", n."projected_growth_rate",
#                        b."growth_percentage_opvalue", b."projected_growth_rate_opvalue",
#                        n."quarterenddate"
#                 FROM fins_all_netsales n
#                 LEFT JOIN fins_all_bps_opvalues b
#                 ON n."seccode" = b."seccode" AND n."quarterenddate" = b."quarterenddate"
#                 WHERE n."seccode" = %(sec_code)s
#                 ORDER BY n."quarterenddate" DESC
#                 LIMIT 1
#                 """,
#                 engine,
#                 params={"sec_code": sec_code},
#             )
#             if company_details.empty:
#                 return jsonify({"message": "Company not found"}), 404
#             portfolio_df = pd.read_sql("SELECT * FROM portfolio ORDER BY seccode ASC", conn).drop(columns=["id"], errors="ignore")
#             updated_portfolio_df = pd.concat([portfolio_df, company_details], ignore_index=True)
#             updated_portfolio_df.sort_values(by="seccode", inplace=True)
#             with engine.begin() as conn:
#                 conn.execute(text("DELETE FROM portfolio;"))
#                 updated_portfolio_df.to_sql("portfolio", conn, if_exists="append", index=False)
#         return jsonify({"message": f"Added {sec_code} to Portfolio"}), 200
#     except Exception as e:
#         return jsonify({"message": f"Error adding to portfolio: {e}"}), 500

# @portfolio_bp.route('/remove_from_portfolio', methods=['POST'])
# def remove_from_portfolio():
#     seccode = request.form.get('seccode')
#     if not seccode:
#         return jsonify({"message": "SecCode is required"}), 400
#     try:
#         with engine.begin() as conn:
#             result = conn.execute(text('DELETE FROM "portfolio" WHERE "seccode" = :seccode'), {"seccode": seccode})
#             rows_affected = result.rowcount
#         if rows_affected > 0:
#             return jsonify({"message": f"Removed record with SecCode {seccode} from Portfolio"}), 200
#         else:
#             return jsonify({"message": f"Record with SecCode {seccode} not found in Portfolio"}), 404
#     except Exception as e:
#         return jsonify({"message": f"Error removing from portfolio: {e}"}), 500



from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import text
import pandas as pd
#from application.backend.db_connect import get_database_engine
from application.backend.engine import engine

# Blueprint for Portfolio
recordhigh_bp = Blueprint('recordhigh', __name__)
#engine = get_database_engine()

@recordhigh_bp.route('/recordhigh')
def view_recordhigh():
    query = 'SELECT * FROM "recordhigh" ORDER BY "seccode" ASC'
    with engine.connect() as conn:
        recordhigh_df = pd.read_sql(query, conn)
    return render_template('recordhigh.html', recordhigh=recordhigh_df.to_dict('records'))

@recordhigh_bp.route('/add_to_recordhigh', methods=['POST'])
def add_to_recordhigh():
    sec_code = request.form.get('seccode')
    if not sec_code:
        return jsonify({"message": "seccode is required"}), 400
    query = """SELECT COUNT(1) FROM recordhigh WHERE "seccode" = :sec_code"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"sec_code": sec_code})
            count = result.scalar()
            if count > 0:
                return jsonify({"message": f"Sec Code {sec_code} is already in the recordhigh."}), 200
            company_details = pd.read_sql(
                """
                SELECT n."seccode", n."companyname", n."fiscalyearend", n."quarter",
                       n."growth_percentage", n."projected_growth_rate",
                       b."growth_percentage_opvalue", b."projected_growth_rate_opvalue",
                       n."quarterenddate"
                FROM "u_fins_all_netsales" n
                LEFT JOIN "u_fins_all_bps_opvalues" b
                ON n."seccode" = b."seccode" AND n."quarterenddate" = b."quarterenddate"
                WHERE n."seccode" = %(sec_code)s
                ORDER BY n."quarterenddate" DESC
                LIMIT 1
                """,
                engine,
                params={"sec_code": sec_code},
            )
            if company_details.empty:
                return jsonify({"message": "Company not found"}), 404
            recordhigh_df = pd.read_sql("SELECT * FROM recordhigh ORDER BY seccode ASC", conn).drop(columns=["id"], errors="ignore")
            updated_recordhigh_df = pd.concat([recordhigh_df, company_details], ignore_index=True)
            updated_recordhigh_df.sort_values(by="seccode", inplace=True)
            with engine.begin() as conn:
                conn.execute(text("DELETE FROM recordhigh;"))
                updated_recordhigh_df.to_sql("recordhigh", conn, if_exists="append", index=False)
        return jsonify({"message": f"Added {sec_code} to recordhigh"}), 200
    except Exception as e:
        return jsonify({"message": f"Error adding to RecorHigh: {e}"}), 500

@recordhigh_bp.route('/remove_from_recordhigh', methods=['POST'])
def remove_from_recordhigh():
    seccode = request.form.get('seccode')
    if not seccode:
        return jsonify({"message": "SecCode is required"}), 400
    try:
        with engine.begin() as conn:
            result = conn.execute(text('DELETE FROM "recordhigh" WHERE "seccode" = :seccode'), {"seccode": seccode})
            rows_affected = result.rowcount
        if rows_affected > 0:
            return jsonify({"message": f"Removed record with SecCode {seccode} from RecorHigh"}), 200
        else:
            return jsonify({"message": f"Record with SecCode {seccode} not found in RecorHigh"}), 404
    except Exception as e:
        return jsonify({"message": f"Error removing from RecorHigh: {e}"}), 500