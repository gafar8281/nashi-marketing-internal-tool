# Salla Out-of-Stock Checker

A web app that finds products listed on Salla that no longer have a sticker in the ERP. Upload the two CSV exports, preview the result and download it. No Python knowledge is needed to use it.

## Using the app

1. Upload the **Salla Product Quantities** CSV as File 1. Its column names are on row 2, including `sku_number`.
2. Upload the **ERP sticker** CSV as File 2. Its column names are on row 1, including `sticker_number`.
3. Click **Process Files**, check the preview, then download `salla_out_of_stock_YYYY-MM-DD.csv`.

## How products are matched

1. The number after the last `-` in `sku_number` is taken as the sticker number (`Brh1746640-109250` gives `109250`).
2. Rows without a usable number are skipped. ERP rows without a numeric `sticker_number` are ignored.
3. A Salla product is out of stock if its number isn't in the ERP file.

The output is the original Salla rows plus a `cleaned_sku_number` column.

**Skipped products:** SKUs in other formats can't be checked, such as `Brd3014240/053713` (slash) and `021169-Brd303118` (number at the front). They aren't in the output. The app reports how many were skipped and lists them.

## Run locally

Requires Python 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

`python main.py` still runs the original command-line version on the files in `data/`.

## Deploy to Streamlit Community Cloud

1. Create a repository on GitHub and push this project to it. `data/` and all CSV files are excluded by `.gitignore`.
2. Sign in at [share.streamlit.io](https://share.streamlit.io) with GitHub and choose **Create app**.
3. Select the repository and branch, and set the main file path to `app.py`.
4. Under **Advanced settings**, choose Python **3.12**.
5. Click **Deploy**.

### Keeping the interface clean

Community Cloud adds its own elements to the page. To reduce them:

1. Keep the GitHub repository **private**, which removes the GitHub links. Grant Streamlit access to private repositories if prompted. Community Cloud allows only one app from a private repository per account.
2. In the app's settings, keep sharing set to **public**, otherwise staff will be asked to sign in.
3. Share this link with staff, which hides the toolbar:

   ```text
   https://<your-app>.streamlit.app/?embed=true
   ```

The creator profile and "Hosted with Streamlit" badge belong to the platform and may still appear. Check the result in a private browser window, because the owner's signed-in view shows extra controls.

## Privacy

- The app has no login: anyone with the link can use it, even when the repository is private.
- Uploaded files are held in memory for that browser session and are never written to disk by the app.
- While being processed, files pass through the hosting provider's servers.
- Never commit real data files to the repository.

## Project layout

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface |
| `main.py` | Data-cleaning and matching logic, plus the command-line version |
| `validation.py` | Checks that uploads are the expected files |
