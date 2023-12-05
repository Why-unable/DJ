document.getElementById('fileButton').addEventListener('click', function() {
        document.getElementById('fileInput').click();
      });

      document.getElementById('fileInput').addEventListener('change', function() {
        var fileInput = document.getElementById('fileInput');
        var fileName = document.getElementById('fileName');

        if (fileInput.files.length > 0) {
          fileName.value = fileInput.files[0].name;
          uploadFile(fileInput.files[0]);
        } else {
          fileName.value = '';
        }
      });



