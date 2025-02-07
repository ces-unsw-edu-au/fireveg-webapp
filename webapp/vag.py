
@bp.route('/VA')
@login_required
def va_groups():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    qry = "SELECT rationale_persistence, persistence, count(*) FROM vag.va_groups GROUP BY rationale_persistence, persistence ORDER BY cardinality(rationale_persistence);"
    cur.execute(qry)
    dectree = cur.fetchall()


    qry = "select unnest(persistence) p, unnest(establishment) as e, count(distinct species_code) from vag.va_groups group by p, e ORDER BY p,e"
    cur.execute(qry)
    res = cur.fetchall()
    df = pd.DataFrame(res)
    df=df.rename(columns={0:"Persistence",1:"Establishment",2:"Records"})
    df['Records'] = df['Records'].astype(int)
    tbl=df.pivot(index='Persistence', columns='Establishment', values='Records')
    tbl.fillna(0,inplace=True)

    cur.close()

    return render_template('traits/VA.html', persistence=dectree,rows=tbl.index.values, cols=tbl.columns.values, cats=tbl.astype(int).values.tolist())
