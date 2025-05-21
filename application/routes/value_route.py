

# value_route.py

from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import text
import pandas as pd
from application.backend.engine import engine

# Create Blueprint
value_bp = Blueprint('value', __name__)

@value_bp.route('/value')
def view_value():
    query = 'SELECT * FROM "value" ORDER BY "seccode" ASC'
    try:
        with engine.connect() as conn:
            value_df = pd.read_sql(query, conn)
        
        # Debug: Check if data is fetched
        print("Fetched Data:", value_df)

        return render_template('value.html', value_list=value_df.to_dict('records'))
    except Exception as e:
        return f"Error fetching value data: {e}", 500

@value_bp.route('/add_to_value', methods=['POST'])
def add_to_value():
    sec_code = request.form.get('seccode')
    if not sec_code:
        return jsonify({"message": "SecCode is required"}), 400

    query = """
    SELECT COUNT(1) 
    FROM value 
    WHERE "seccode" = :sec_code
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), {"sec_code": sec_code})
            count = result.scalar()
            if count > 0:
                return jsonify({"message": f"Sec Code {sec_code} is already in the Value list."}), 200

            new_company_details = pd.read_sql("""
                SELECT n."seccode", n."companyname", n."fiscalyearend", n."quarter", n."growth_percentage",
                       n."projected_growth_rate", b."growth_percentage_opvalue", b."projected_growth_rate_opvalue",
                       n."quarterenddate"
                FROM "u_fins_all_netsales" n
                LEFT JOIN "u_fins_all_bps_opvalues" b
                ON n."seccode" = b."seccode" AND n."quarterenddate" = b."quarterenddate"
                WHERE n."seccode" = %(sec_code)s
                ORDER BY n."quarterenddate" DESC
                LIMIT 1
            """, engine, params={"sec_code": sec_code})

            if new_company_details.empty:
                return jsonify({"message": "Company not found"}), 404

            existing_value = pd.read_sql('SELECT * FROM value', conn)
            value_df = pd.concat([existing_value, new_company_details], ignore_index=True)
            value_df.sort_values(by='seccode', inplace=True)
            value_df.drop(columns=['id'], errors='ignore', inplace=True)

            with engine.begin() as conn:
                conn.execute(text('DELETE FROM value'))
                value_df.to_sql('value', conn, if_exists='append', index=False)

        return jsonify({"message": f"Added {sec_code} to Value list"}), 200
    except Exception as e:
        return jsonify({"message": f"Error adding to value: {e}"}), 500

@value_bp.route('/remove_from_value', methods=['POST'])
def remove_from_value():
    sec_code = request.form.get('seccode')
    if not sec_code:
        return jsonify({"message": "SecCode is required"}), 400

    try:
        with engine.begin() as conn:
            result = conn.execute(text('DELETE FROM "value" WHERE "seccode" = :seccode'), {"seccode": sec_code})
        if result.rowcount > 0:
            return jsonify({"message": f"Removed {sec_code} from Value list"}), 200
        else:
            return jsonify({"message": f"{sec_code} not found in Value list"}), 404
    except Exception as e:
        return jsonify({"message": f"Error removing from value: {e}"}), 500
