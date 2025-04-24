import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import numpy as np
import io
from dash.dependencies import Output, Input, State
from dash import dash_table, ctx
#import dash_bootstrap_components as dbc

data = pd.read_csv("data/WA_Fn-UseC_-HR-Employee-Attrition.csv")
data.Education = data.Education.astype(str)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "IBM HR Analytics"

numeric_cols = data.select_dtypes(include='number').columns
education_map = {'1':'Below College', '2': 'College', '3': 'Bachelor', '4': 'Master', '5': 'Doctor'}
overall_colums = {
    "Age": "Age",
    "DailyRate": "Daily Rate",
    "DistanceFromHome": "Distance From Home",
    "HourlyRate": "Hourly Rate",
    "MonthlyIncome": "Monthly Income",
    "MonthlyRate": "Monthly Rate",
    "NumCompaniesWorked": "Num of Companies Worked",
    "PercentSalaryHike": "Percent Salary Hike",
    "PerformanceRating": "Performance Rating",
    "StockOptionLevel": "Stock Option Level",
    "TotalWorkingYears": "Total Working Years",
    "TrainingTimesLastYear": "Training Times Last Year",
    "WorkLifeBalance": "Work Life Balance",
    "YearsAtCompany": "Years At Company",
    "YearsInCurrentRole": "Years In Current Role",
    "YearsSinceLastPromotion": "Years Since Last Promotion",
    "YearsWithCurrManager": "Years With Current Manager",
}

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📊", className="header-emoji"),
                html.H2(
                    children="IBM HR Analytics Employee Attrition & Performance", className="header-title"
                ),
                html.P(
                    children="Analysis of the impact of employee experience and education on key performance indicators",
                    className="header-description",
                ),
            ],
            className="header",
        ),

        html.Div(
            [
                html.P("KPI", className="card-title"),
                html.P("0", id="metrics-cards", className="card-text"),
            ],
            className="card"
        ),
        html.Div(
            children=[
                html.Button("Filters", id="filter-button", n_clicks=0, className="filter-toggle"),
                html.Button("Dowload", id="download-button", n_clicks=0, className="download-toggle"),
            ],
            className="toggle-button",
        ),

        html.Div(
                children=[
                    html.Div(children="Filters", className="menu-filter-title"),
                    html.Div(
                        children=[
                            html.Div(children="Department", className="filter-title"),
                            dcc.Dropdown(
                                id="department-filter",
                                options=[
                                    {"label": car_type, "value": car_type} for car_type in data.Department.unique()
                                ],
                                value="Sales",
                                clearable=False,
                                searchable=False,
                                className="dropdown",
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Div(children="Job Role", className="filter-title"),
                            dcc.Dropdown(
                                id="job-role-filter",
                                clearable=False,
                                searchable=False,
                                className="dropdown",
                            ),
                        ],

                    ),
                    html.Div(
                        children=[
                            html.Div(children="Attrition", className="filter-title"),
                            dcc.RadioItems(
                                id="attrition-checklist",
                                options=[{"label": role, "value": role} for role in data["Attrition"].unique()],
                                value="Yes",
                                labelStyle={"display": "block"},
                                className="dropdown",
                            ),
                        ]
                    ),
                ],
        className="menu",
        id="menu",
        ), 
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="department-chart", config={"displayModeBar": False},
                    ),
                    className="graph",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="job-role-chart", config={"displayModeBar": False},
                    ),
                    className="graph",
                ),
            ],
            className="wrapper-graph",
        ),
        html.Div(
            children=[
                dash_table.DataTable(
                    id='summary-table',
                    sort_action='native',
                    style_cell={
                        'textAlign': 'center',
                        'padding': '8px',
                        'fontFamily': 'Arial'
                    },
                    style_header={
                        'backgroundColor': '#f4f4f4',
                        'fontWeight': 'bold',
                        'whiteSpace': 'pre-line',
                    },
                    filter_action="native",
                ),
                dash_table.DataTable(
                    id='overall-table',
                    sort_action='native',
                    style_cell={
                        'textAlign': 'center',
                        'padding': '8px',
                        'fontFamily': 'Arial'
                    },
                    style_header={
                        'backgroundColor': '#f4f4f4',
                        'fontWeight': 'bold'
                    },
                ),
                dcc.Download(id="download-excel"),
            ],
            className = "wrapper-table"
        )
    ],
)

@app.callback(
    Output("download-excel", "data"),
    Input("download-button", "n_clicks"),
    Input('summary-table', 'data'),
    Input('overall-table', 'data'),
    prevent_initial_call=True
)
def download_excel(n_clicks, summary_table_data, overall_table_data):
    if ctx.triggered_id == "download-button":
        df1_updated = pd.DataFrame(summary_table_data)
        df2_updated = pd.DataFrame(overall_table_data)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df1_updated.to_excel(writer, sheet_name='Summary', index=False)
            df2_updated.to_excel(writer, sheet_name='Overall', index=False)

        output.seek(0)
        
        return dcc.send_bytes(output.getvalue(), "all_sheets.xlsx")
    return None

@app.callback(
    Output("menu", "style"),
    [Input("filter-button", "n_clicks")],
    [State("menu", "style")]
)
def toggle_sidebar(n_clicks, current_style):
    if n_clicks % 2 == 1:
        return {"width": "250px", "position": "fixed", "left": "0", "top": "0", "height": "100vh", "background-color": "#f4f4f4", "transition": "0.3s"}
    else:
        return {"width": "0", "position": "fixed", "left": "-250px", "top": "0", "height": "100vh", "background-color": "#f4f4f4", "transition": "0.3s"}


@app.callback(
    [Output("job-role-filter", "options"), Output("job-role-filter", "value"),],
    [
        Input("department-filter", "value"), 
    ],
)
def update_dropdown(department_type):
    job_roles =    [
            {"label": job_role, "value": job_role}
            for job_role in data[data.Department == department_type].JobRole.unique()
            ]
    value = job_roles[0]["value"]
    return job_roles, value


@app.callback(
    [Output("department-chart", "figure"), Output("job-role-chart", "figure")],
    [
        Input("department-filter", "value"), 
        Input("job-role-filter", "value"),
        Input("attrition-checklist", "value"),
    ],
)
def update_charts(department_type, job_role_type, attrition_value):
    mask = (
        (data.Department == department_type) &
        (data.JobRole == job_role_type) &
        (data.Attrition == attrition_value)
    )
    filtered_data = data.loc[mask, :]

    grouped = filtered_data.groupby("TotalWorkingYears")["MonthlyIncome"].mean().reset_index()

    department_chart_figure = {
        "data": [
            {
                "x": grouped["TotalWorkingYears"],
                "y": grouped["MonthlyIncome"],
                "type": "bar",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
                'orientation': 'v',
            }
        ],
        "layout": {
            "title": {"text": "Average income by experience years", "x": 0.05, "xanchor": "left"},
            "xaxis": {"title": "Стаж (лет)", "tickmode": "linear"},
            "yaxis": {"title": "Доход", "tickprefix": "$"},
            "colorway": ["#17B897"],
        }
    }


    grouped_education = filtered_data.groupby("Education")["MonthlyIncome"].mean().reset_index()
    x_vals = grouped_education["Education"].map(education_map)

    job_role_chart_figure = {
        "data": [
            {
                "x": x_vals,
                "y": grouped_education["MonthlyIncome"],
                "type": "bar",
                'orientation': 'v', 
            },
        ],
        "layout": {
            "title": {
                "text": "Average income by education level", "x": 0.05,"xanchor": "left",
            },
            "xaxis": {"fixedrange": True, "categoryarray": [*education_map.values()]},
            "yaxis": {"fixedrange": True, "tickprefix": "$"},
            "colorway": ["#E12D39"],
        },
    }

    return department_chart_figure, job_role_chart_figure


@app.callback(
    [Output('overall-table', 'data'), Output('summary-table', 'data'), Output('summary-table', 'columns'),],
    [
        Input("department-filter", "value"), 
        Input("job-role-filter", "value"),
        Input("attrition-checklist", "value"),
    ],
)
def update_tadles(department_type, job_role_type, attrition_value):
    mask_summary = (
        (data.Department == department_type) &
        (data.JobRole == job_role_type)
    )

    filtered_data_summary = data.loc[mask_summary, :]

    summary_df = filtered_data_summary.groupby(['Education', 'EducationField']).agg({
        'MonthlyIncome': 'mean',
        'OverTime': lambda x: (x == 'Yes').mean()*100,
        'Attrition': lambda x: (x == 'Yes').mean()*100,
        'TotalWorkingYears': 'mean',
        'PercentSalaryHike': 'mean',
        'PerformanceRating': 'mean',
        'YearsInCurrentRole': 'mean',
        'YearsSinceLastPromotion': 'mean',
    }).reset_index().round(2)
    summary_df.Education = summary_df.Education.map(education_map)

    colums_summary =[
        {"name": "Education\nGrade", "id": "Education"},
        {"name": "Education\nField", "id": "EducationField"},
        {"name": "Monthly\nIncome $", "id": "MonthlyIncome"},
        {"name": "Over\nTime\n%", "id": "OverTime"},
        {"name": "Attrition\n%", "id": "Attrition"},
        {"name": "Total\nWorking\nYears", "id": "TotalWorkingYears"},
        {"name": "Percent\nSalary\nHike %", "id": "PercentSalaryHike"},
        {"name": "Performance\nRating\n(1-4)", "id": "PerformanceRating"},
        {"name": "Years In\nCurrent Role", "id": "YearsInCurrentRole"},
        {"name": "Years Since\nLast Promotion", "id": "YearsSinceLastPromotion"},

    ]

    filtered_data_overall = filtered_data_summary.loc[filtered_data_summary.Attrition == attrition_value, :]
    overall_df = pd.DataFrame({
        'Target': numeric_cols,
        'Average': filtered_data_overall[numeric_cols].mean().round(2).values,
        'Average deviation': filtered_data_overall[numeric_cols].std().round(2).values,
        'Min': filtered_data_overall[numeric_cols].min().values,
        'Max': filtered_data_overall[numeric_cols].max().values
        })
    overall_df = overall_df[overall_df["Target"].isin(list(overall_colums.keys()))]
    overall_df.Target = overall_df.Target.map(overall_colums)
    return overall_df.to_dict("records"), summary_df.to_dict("records"), colums_summary


@app.callback(
    Output("metrics-cards", "children"),
    Input("department-filter", "value"), 
    Input("job-role-filter", "value"),
    Input("attrition-checklist", "value"),
)
def update_cards(dept, role, attr):
    filtered_df = data.copy()
    
    if dept and isinstance(dept, str): dept = [dept]  
    if role and isinstance(role, str): role = [role]
    if attr and isinstance(attr, str): attr = [attr]
    
    if dept is None: dept = []
    if role is None: role = []
    if attr is None: attr = []

    if dept:
        filtered_df = filtered_df[filtered_df["Department"].isin(dept)]
    if role:
        filtered_df = filtered_df[filtered_df["JobRole"].isin(role)]
    if attr:
        filtered = filtered_df[filtered_df["Attrition"].isin(attr)]
    
    mean_income = filtered["MonthlyIncome"].mean()
    mean_age = filtered["Age"].mean()
    mean_years = filtered["TotalWorkingYears"].mean()
    count = len(filtered)
    
    gender_count = filtered["Gender"].value_counts(normalize=True) * 100
    female_percentage = gender_count.get("Female", 0)
    male_percentage = gender_count.get("Male", 0)
    
    mean_years_at_company = filtered["YearsAtCompany"].mean()

    attrition_count = filtered_df["Attrition"].value_counts(normalize=True) * 100
    yes_percentage = attrition_count.get("Yes", 0)
    
    filter_info = [
        f"Department: {', '.join(dept) if dept else 'All'}",
        f"Job Role: {', '.join(role) if role else 'All'}",
        f"Attrition: {', '.join(attr) if attr else 'All'}"
    ]
    def make_card(title, value, other):
        return html.Div([
            html.P(f"{title}: {value:,.2f}{other}" if isinstance(value, float) else f"{title}: {value}{other}", className="card-value"),
            ]
            )
    
    return [
        make_card("Average income", mean_income, "$"),
        make_card("Average age", mean_age, ''),
        make_card("Work experience", mean_years, ''),
        make_card("Percentage of women", female_percentage, '%'),
        make_card("Percentage of men", male_percentage, '%'),
        make_card("Average years with the company", mean_years_at_company, ''),
        make_card("Number of employees", count, ''),
        make_card("Employee attrition", yes_percentage, '%'),
        make_card("Standart working hours", 80, "")
    ]

if __name__=="__main__":
    app.run(debug=True)
    