import sqlite3
import flask

app = flask.Flask(__name__)

def get_db():
    db = sqlite3.connect('jpsalon.db')
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/addmember')
def addmember():
    db = get_db()
    cursor = db.execute('SELECT seq FROM sqlite_sequence WHERE name = "Members"') #to get ID of most recent member
    x = cursor.fetchall() #integer format expected
    mi =  int(x[0][0]) + 1
    return flask.render_template('addmember.html',mi=mi)

@app.route('/addedmember', methods=['POST']) #add new member, 10% discount btw
def addedmember():
    db = get_db()
    cursor = db.execute('SELECT seq FROM sqlite_sequence WHERE name = "Members"') #to get ID of most recent member
    x = cursor.fetchall() #integer format expected
    mi = int(x[0][0]) + 1
    n = flask.request.form['name']
    g = flask.request.form['gender']
    e = flask.request.form['email']
    c = flask.request.form['contact']
    a = flask.request.form['addr']
    db.execute('INSERT INTO Members (memberID, memberName, Gender, Email, Contact, Address) VALUES (?,?,?,?,?,?)',(mi, n, g, e, c, a))
    db.commit()
    db.close()
    return flask.render_template('addedmember.html', n=n)

@app.route('/updatedetails') #page to choose between updating member's email OR mobile no.
def updatedetails():
    db = get_db()
    cursor = db.execute('SELECT memberID FROM Members ORDER BY memberID DESC')
    li = cursor.fetchone()
    li = li[0]
    cursor = db.execute('SELECT memberID FROM Members')
    fi = cursor.fetchone()
    fi = fi[0]
    return flask.render_template('updatedetails.html', fi=fi, li=li)

@app.route('/detailsupdated', methods=['POST'])
def detailsupdated():
    db = get_db()
    i = flask.request.form['memberID']
    nc = flask.request.form['newcontact']
    ne = flask.request.form['newemail']
    db = get_db()
    if nc != '00000000':
        db.execute('UPDATE Members SET Contact = ? WHERE memberID = ?',(nc,i))
    elif ne != 'NULL':
        db.execute('UPDATE Members SET Email = ? WHERE memberID = ?',(ne,i))
    db.commit()
    db.close()
    return flask.render_template('detailsupdated.html', i=i)

@app.route('/addtransaction')
def addtransaction():            #add a new business transaction
    return flask.render_template('addtransaction.html')

@app.route('/transactionadded', methods=['POST'])
def transactionadded():
    db = get_db()
    cursor = db.execute('SELECT seq FROM sqlite_sequence WHERE name = "Transactions"')
    row = cursor.fetchone()
    ii = int(row[0] + 1)
    d = flask.request.form['date'] #drop-down lists for dd,mm,yyyy with <select>
    mi = flask.request.form['memberID']
    n = flask.request.form['name']

    t = []
    if flask.request.form.get('check1') == '':
        t.append(flask.request.form['check1'])
    if flask.request.form.get('check2') == '':
        t.append(flask.request.form['check2'])
    if flask.request.form.get('check3') == '':
        t.append(flask.request.form['check3'])
    if flask.request.form.get('check4') == '':
        t.append(flask.request.form['check4'])
    if flask.request.form.get('check5') == '':
        t.append(flask.request.form['check5'])
    if flask.request.form.get('check6') == '':
        t.append(flask.request.form['check6'])
    if flask.request.form.get('check7') == '':
        t.append(flask.request.form['check7'])
    if flask.request.form.get('check8') == '':
        t.append(flask.request.form['check8'])
    if flask.request.form.get('check9') == '':
        t.append(flask.request.form['check9'])
    prices = []
    for i in t:
        cursor = db.execute('SELECT price FROM Service WHERE type=?',(i))
        rows = cursor.fetchall()
        prices.append(rows[0])

    
    ############################
    #need to calc price per type given in pdf
    ta = 0.0
    for i in prices:
        ta += i
    if mi != 0: #if member
        ta = .9*ta
    db.execute('INSERT INTO Transactions (InvoiceID, Datee, memberID, name, Total_Amount) VALUES (?,?,?,?,?)',(ii,d,mi,n,ta))
    db.commit()
    for i in t:
        db.execute('INSERT INTO TransactionDetails (InvoiceID, type) VALUES (?,?)', (ii,i))
        db.commit()
    db.close()
    return flask.render_template('transactionadded.html', ii=ii)

@app.route('/dailytransactions')
def dailytransactions():        #get date
    return flask.render_template('dailytransactions.html')
    
@app.route('/viewdailytransactions', methods=['POST'])
def viewdailytransactions():        #view dailytransactions
    db = get_db()
    date = flask.request.form['date']
    d,m,y = date.split('-')
    date = y+'-'+m+'-'+d
    cursor = db.execute('SELECT * FROM Transactions WHERE Datee = ?',(date,))
    rows = cursor.fetchall()
    ii,mi,d,n,ta = [],[],[],[],[]
    for i in rows:
        ii += [i[0]]
        mi += [i[1]]
        d += [i[2]]
        n += [i[3]]
        ta += [i[4]]
    t = []
    for j in rows:
        ii.append(j[0][0])
    for j in ii:
        cursor = db.execute('SELECT type FROM TransactionDetails WHERE InvoiceID = ?',(j))
        row = cursor.fetchone()
        t.append(row[0])
    db.close()
    return flask.render_template('viewdailytransactions.html', rows=rows, t=t, ii=ii,mi=mi,d=d,n=n,ta=ta)


@app.route('/monthlysalesrevenue') #view monthly sales revenue
def monthlysalesrevenue():
    return flask.render_template('monthlysalesrevenue.html')

@app.route('/viewmonthlysalesrevenue', methods=['POST']) #view monthly sales revenue
def viewmonthlysalesrevenue():
    db = get_db()
    m = flask.request.form['month']
    y = flask.request.form['year']
    startdate = str(y)+'-'+str(m)+'-01'
    enddate = str(y)+'-'+(str(int(m)+1))+'-01'
    cursor = db.execute('SELECT Total_Amount FROM Transactions WHERE Datee >= ? AND Datee <= ?',(startdate, enddate))
    rows = cursor.fetchall()
    ta = 0.0
    for i in rows:
        ta += i[0]
    db.close()
    return flask.render_template('viewmonthlysalesrevenue.html',y=y,m=m, ta=ta)
@app.route('/membertransactionhistory') #view member's transaction history
def membertransactionhistory():
    db = get_db()
    cursor = db.execute('SELECT memberID FROM Members ORDER BY memberID DESC')
    li = cursor.fetchone()
    li = li[0]
    cursor = db.execute('SELECT memberID FROM Members')
    fi = cursor.fetchone()
    fi = fi[0]
    db.close()
    return flask.render_template('membertransactionhistory.html', fi=fi, li=li,)

@app.route('/viewmembertransactionhistory', methods=['POST'])
def viewmembertransactionhistory():
    db = get_db()
    cursor = db.execute('SELECT InvoiceID, Datee, Total_Amount FROM Transactions WHERE memberID = ?',(flask.request.form['memberID']))
    rows = cursor.fetchall()
    i,d,ta = [],[],[]
    t = []
    for j in rows:
        i += [int(j[0])]
        d += [j[1]]
        ta = ['$'+str(f"{j[2]:.2f}")]
    for j in i:
        cursor = db.execute('SELECT type from TransactionDetails WHERE InvoiceID = ?', (j))
        
        
        row = cursor.fetchone()
        t += row[0]
        ####need to code for showing typename
    
    db.close()
    return flask.render_template('viewmembertransactionhistory.html', rows=rows, i=i,d=d,ta=ta,t=t)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
