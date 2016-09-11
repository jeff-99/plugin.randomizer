module.exports = function(grunt) {

  config = grunt.file.readJSON('config.json')
  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    watch: {
      all: {
        files: [
          'src/plugin.randomizer/**'
        ],
        tasks: ['copy']
      }
    },
    copy: {
      main: {
        files: [
          {expand: true, cwd: 'src/', src: ['plugin.randomizer/**'], dest: config["kodi"] + '/addons'}
        ],
      },
    },
    compress: {
      main: {
        options: {
          archive: 'bin/plugin.randomizer.zip'
        },
        files: [
          {expand: true, cwd: 'src/', src: ['plugin.randomizer/**'], dest: '/'},
        ]
      }
    }
  });

  // Load the Grunt plugins.
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-compress');

  // Register the default tasks.
  grunt.registerTask('default', ['watch']);
  grunt.registerTask('zip', ['compress']);
};