
from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import text
import pandas as pd
#from application.backend.db_connect import get_database_engine
from application.backend.engine import engine


# Create Blueprint
growth_bp = Blueprint('growth', __name__)
#engine = get_database_engine()

@growth_bp.route('/growth')
def view_growth():
    query = 'SELECT * FROM "growth" ORDER BY "seccode" ASC'
    with engine.connect() as conn:
        growth_df = pd.read_sql(query, conn)
    return render_template('growth.html', growth=growth_df.to_dict('records'))

@growth_bp.route('/add_to_growth', methods=['POST'])
def add_to_growth():
    sec_code = request.form.get('seccode')
    if not sec_code:
        return jsonify({"message": "SecCode is required"}), 400

    try:
        with engine.connect() as conn:
            # Check if already exists
            exists_query = text("""
                SELECT COUNT(1) FROM growth WHERE "seccode" = :sec_code
            """)
            count = conn.execute(exists_query, {"sec_code": sec_code}).scalar()
            if count > 0:
                return jsonify({"message": f"Sec Code {sec_code} is already in the growth."}), 200

            # Safely fetch the latest company data
            query = text("""
                SELECT n."seccode", n."companyname", n."fiscalyearend", n."quarter", n."growth_percentage",
                       n."projected_growth_rate", b."growth_percentage_opvalue", b."projected_growth_rate_opvalue",
                       n."quarterenddate"
                FROM "u_fins_all_netsales" n
                LEFT JOIN "u_fins_all_bps_opvalues" b
                ON n."seccode" = b."seccode" AND n."quarterenddate" = b."quarterenddate"
                WHERE n."seccode" = :sec_code
                ORDER BY n."quarterenddate" DESC
                LIMIT 1
            """)
            new_company_details = pd.read_sql(query, conn, params={"sec_code": sec_code})

            if new_company_details.empty:
                return jsonify({"message": "Company not found"}), 404

            # Insert into 'growth' table
            existing_growth = pd.read_sql('SELECT * FROM growth', conn)
            growth_df = pd.concat([existing_growth, new_company_details], ignore_index=True)
            growth_df.sort_values(by='seccode', inplace=True)
            growth_df.drop(columns=['id'], errors='ignore', inplace=True)

        # Replace all records with the updated one
        with engine.begin() as conn:
            conn.execute(text('DELETE FROM growth'))
            growth_df.to_sql('growth', conn, if_exists='append', index=False)

        return jsonify({"message": f"Added {sec_code} to growth"}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Error adding to growth: {e}"}), 500

@growth_bp.route('/remove_from_growth', methods=['POST'])
def remove_from_growth():
    sec_code = request.form.get('seccode')
    if not sec_code:
        return jsonify({"message": "SecCode is required"}), 400

    try:
        with engine.begin() as conn:
            result = conn.execute(text('DELETE FROM "growth" WHERE "seccode" = :seccode'), {"seccode": sec_code})
        if result.rowcount > 0:
            return jsonify({"message": f"Removed {sec_code} from growth"}), 200
        else:
            return jsonify({"message": f"{sec_code} not found in growth"}), 404
    except Exception as e:
        return jsonify({"message": f"Error removing from growth: {e}"}), 500
