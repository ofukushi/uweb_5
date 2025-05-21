

from flask import Blueprint, request, jsonify, render_template
from sqlalchemy import text
import pandas as pd
#from application.backend.db_connect import get_database_engine
from application.backend.engine import engine
# Create a Blueprint for record_w52_high
record_w52_high_bp = Blueprint('record_w52_high', __name__)

# Initialize the database engine
#engine = get_database_engine()

@record_w52_high_bp.route('/record_w52_high')
def record_w52_high():
    query = 'SELECT * FROM "record_w52_high" ORDER BY "seccode" ASC'
    try:
        # Fetch data from the database
        record_w52_df = pd.read_sql(query, engine)

        # Format the timestamp
        record_w52_df['timestamp'] = pd.to_datetime(record_w52_df['timestamp']).dt.tz_convert('Asia/Tokyo').dt.strftime('%Y-%m-%d %H:%M')

        # Pass data to the template
        return render_template('record_w52_high.html', records=record_w52_df.to_dict('records'))
    except Exception as e:
        print(f"Error fetching record_w52_high data: {e}")
        return "Error loading records.", 500

@record_w52_high_bp.route('/remove_from_record_w52_high', methods=['POST'])
def remove_from_record_w52_high():
    seccode = request.form.get('seccode')

    if not seccode:
        return jsonify({"message": "SecCode is required"}), 400

    try:
        with engine.begin() as conn:
            # Delete the record
            result = conn.execute(text('DELETE FROM "record_w52_high" WHERE "seccode" = :seccode'), {"seccode": seccode})
            rows_affected = result.rowcount

        if rows_affected > 0:
            return jsonify({"message": f"Removed record with SecCode {seccode} from record_w52_high"}), 200
        else:
            return jsonify({"message": f"Record with SecCode {seccode} not found in record_w52_high"}), 404

    except Exception as e:
        print(f"Error removing record with SecCode {seccode}: {e}")
        return jsonify({"message": "Error removing from record_w52_high."}), 500
