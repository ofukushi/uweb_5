
from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import text
import pandas as pd
from application.backend.engine import engine

dividend_bp = Blueprint('dividend', __name__)

@dividend_bp.route('/dividend')
def view_dividend():
    query = 'SELECT * FROM "dividend" ORDER BY "seccode" ASC'
    with engine.connect() as conn:
        dividend_df = pd.read_sql(query, conn)
    return render_template('dividend.html', dividend=dividend_df.to_dict('records'))

@dividend_bp.route('/add_to_dividend', methods=['POST'])
def add_to_dividend():
    sec_code = request.form.get('seccode')
    if not sec_code:
        return jsonify({"message": "seccode is required"}), 400

    check_query = 'SELECT COUNT(1) FROM dividend WHERE "seccode" = :sec_code'
    try:
        with engine.connect() as conn:
            count = conn.execute(text(check_query), {"sec_code": sec_code}).scalar()
            if count > 0:
                return jsonify({"message": f"Sec Code {sec_code} is already in the dividend table."}), 200

            # Pull latest dividend data from bps_opvalues
            company_details = pd.read_sql(
                """
                SELECT
                    seccode, companyname, fiscalyearend,
                    adjusted_divannual_for_chart AS dividend_amount,
                    NULL AS dividend_yield
                FROM (
                    SELECT *,
                        ROW_NUMBER() OVER (PARTITION BY seccode ORDER BY quarterenddate DESC) as rn
                    FROM u_fins_all_bps_opvalues
                    WHERE seccode = %(sec_code)s
                ) sub
                WHERE rn = 1
                """,
                engine,
                params={"sec_code": sec_code}
            )

            if company_details.empty:
                return jsonify({"message": "Company not found"}), 404

            current_df = pd.read_sql("SELECT * FROM dividend ORDER BY seccode ASC", conn).drop(columns=["id"], errors="ignore")
            updated_df = pd.concat([current_df, company_details], ignore_index=True)
            updated_df.sort_values(by="seccode", inplace=True)

            with engine.begin() as trans_conn:
                trans_conn.execute(text("DELETE FROM dividend;"))
                updated_df.to_sql("dividend", trans_conn, if_exists="append", index=False)

        return jsonify({"message": f"Added {sec_code} to dividend"}), 200

    except Exception as e:
        print(f"DEBUG: {e}")  # Add this line
        return jsonify({"message": f"Error adding to Dividend: {e}"}), 500

@dividend_bp.route('/remove_from_dividend', methods=['POST'])
def remove_from_dividend():
    seccode = request.form.get('seccode')
    if not seccode:
        return jsonify({"message": "seccode is required"}), 400
    try:
        with engine.begin() as conn:
            result = conn.execute(text('DELETE FROM "dividend" WHERE "seccode" = :seccode'), {"seccode": seccode})
            if result.rowcount > 0:
                return jsonify({"message": f"Removed record with seccode {seccode} from dividend"}), 200
            else:
                return jsonify({"message": f"No record found with seccode {seccode}"}), 404
    except Exception as e:
        return jsonify({"message": f"Error removing from Dividend: {e}"}), 500
