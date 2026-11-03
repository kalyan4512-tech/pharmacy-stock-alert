from datetime import datetime, date

class MedicineValidator:
    """Validator and sanitization helper for medicine data."""

    @staticmethod
    def validate(data):
        errors = []

        # Name
        name = data.get("name", "").strip()
        if not name:
            errors.append("Medicine name is required.")

        # Category
        category = data.get("category", "").strip()
        if not category:
            errors.append("Category is required.")

        # Batch Number
        batch_number = data.get("batch_number", "").strip()
        if not batch_number:
            errors.append("Batch number is required.")

        # Manufacturer
        manufacturer = data.get("manufacturer", "").strip()
        if not manufacturer:
            errors.append("Manufacturer is required.")

        # Quantity
        try:
            quantity = int(data.get("quantity", 0))
            if quantity < 0:
                errors.append("Quantity cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid integer.")

        # Minimum Threshold
        try:
            min_threshold = int(data.get("min_threshold", 10))
            if min_threshold < 0:
                errors.append("Minimum threshold cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Minimum threshold must be a valid integer.")

        # Purchase Price
        try:
            purchase_price = float(data.get("purchase_price", 0.0))
            if purchase_price < 0:
                errors.append("Purchase price cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Purchase price must be a valid number.")

        # Selling Price
        try:
            selling_price = float(data.get("selling_price", 0.0))
            if selling_price < 0:
                errors.append("Selling price cannot be negative.")
        except (ValueError, TypeError):
            errors.append("Selling price must be a valid number.")

        # Dates
        mfg_date_str = data.get("mfg_date", "").strip()
        expiry_date_str = data.get("expiry_date", "").strip()

        mfg_date = None
        exp_date = None

        if not mfg_date_str:
            errors.append("Manufacturing date is required.")
        else:
            try:
                mfg_date = datetime.strptime(mfg_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Manufacturing date format must be YYYY-MM-DD.")

        if not expiry_date_str:
            errors.append("Expiry date is required.")
        else:
            try:
                exp_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Expiry date format must be YYYY-MM-DD.")

        if mfg_date and exp_date and exp_date <= mfg_date:
            errors.append("Expiry date must be after manufacturing date.")

        # Supplier
        supplier = data.get("supplier", "").strip()
        if not supplier:
            errors.append("Supplier name is required.")

        return errors

