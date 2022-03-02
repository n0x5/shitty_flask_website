** Date: 2022-03-01 **

# this is my first post

## syntax highlighting test:

    #!/usr/bin/python
    import flask
    @app.route('/blog2')
    def blog2_index():
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), 'posts')):
        results3 = [os.path.join(root, post1) for post1 in files]
        results3.sort(key=os.path.getmtime, reverse=True)
        results2 = [os.path.basename(fn).replace('.md', '') for fn in results3]

    return render_template('blog2index.html', results2=results2)


** yeehaw **
