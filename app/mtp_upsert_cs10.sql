-- Function: mtp_upsert_cs10(json)

-- DROP FUNCTION mtp_upsert_cs10(json);

CREATE OR REPLACE FUNCTION mtp_upsert_cs10(i_json json)
  RETURNS json AS
$BODY$

#
# allow set NULL
#

#init
cols = []
vals = []
v_sql = ""

result = null

#input
v_table = i_json.table

# column name of primark key
v_pkey = i_json.pkey

#modified on 2014-05-10 20:50:19
#set default column name of primary key
if not v_pkey
    v_pkey = "id"

v_id = i_json.columns.id

languageid = i_json.context.languageid

v_user = i_json.context.user

v_rowversion = i_json.columns.rowversion

#if not v_rowversion
#    v_rowversion = 1

if not languageid
    #throw("please provide languageid")
    return {"error":"please provide languageid"}

for key in Object.keys(i_json.columns)

    if key == v_pkey
        if i_json.columns[v_pkey] != null and i_json.columns[v_pkey] != ''
            #update  = true
            v_id = i_json.columns[v_pkey]
        else
            continue



    if key == 'texths'
        val = i_json.columns[key]

        if val != null
            #if no value for hstore then bypass
            cols.push(key)

            if typeof(val) == 'string'
                val = val.replace("'","''") # escape single quote
            v = "hstore('#{languageid}', '#{val}')"
            vals.push(v)
        else
            cols.push(key)
            v = "hstore('#{languageid}', '')"
            vals.push(v)
    else
        cols.push(key)
        val = i_json.columns[key]

        if typeof(val) == 'string'

            y = val.split('::')

            if y.length == 2
                v = "'#{y[0]}'::#{y[1]}"
                vals.push(v)

            else
                val = val.replace("'","''")  # escape single quote
                v = "'#{val}'"
                vals.push(v)
        else
            vals.push(val)

if v_id
    #build update sql

    #c= cols.join(",")
    #v = vals.join(",")

    fields = []

    for i in [0 ..cols.length-1]

        col = cols[i]
        val = vals[i]

        if val == null
            fields.push("#{col} = NULL")
            continue

        if col in [v_pkey, "id","seq", "modifiedon","modifiedby","createdon","createdby","rowversion"]
            continue

        if col == "texths"
            fields.push("#{col} = #{col}||#{val}")
            #fields.push("#{col} = #{val}")
        else

            fields.push("#{col} = #{val}")

    setfields = fields.join(", ")

    v_sql = "update #{v_table} set #{setfields}, modifiedon = now(), modifiedby = '#{v_user}', rowversion = rowversion + 1
        where #{v_pkey} = '#{v_id}' returning #{v_pkey}, modifiedon, modifiedby, createdon, createdby, rowversion"

else
    #build insert sql

    t_cols = []
    t_vals = []

    for i in [0 .. cols.length-1 ]

        col = cols[i]
        val = vals[i]
        if val == null
            continue
        if col in ["seq", "modifiedon", "modifiedby", "createdon", "createdby", "rowversion"]
            #alert?
            continue
        else
            t_cols.push(col)
            t_vals.push(val)

    v_cols= t_cols.join(", ")

    v_vals = t_vals.join(", ")

    v_sql = "insert into #{v_table} (#{v_cols}, modifiedon, modifiedby, createdon, createdby)
            values(#{v_vals}, now(), '#{v_user}', now(), '#{v_user}') returning #{v_pkey}, modifiedon, modifiedby, createdon, createdby, rowversion"

try
    result = plv8.execute( v_sql )
catch err
    plv8.elog(DEBUG, v_sql)
    msg = "#{err},#{v_sql}"
    #return {"sql":v_sql,"error":msg}
    throw(msg)

return {"returning":result, "sql":v_sql}

$BODY$
  LANGUAGE plcoffee VOLATILE
  COST 100;
ALTER FUNCTION mtp_upsert_cs10(json)
  OWNER TO mabotech;
