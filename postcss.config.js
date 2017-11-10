module.exports = {
    plugins: [
        require('autoprefixer')({
            browsers: ['last 2 versions', 'Firefox >= 20', 'ie >= 9']
        }) 
    ]
}