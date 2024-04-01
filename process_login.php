<?php
// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Connect to MySQL database
    $servername = "localhost"; // Change this to your MySQL server hostname
    $username = "your_username"; // Change this to your MySQL username
    $password = "your_password"; // Change this to your MySQL password
    $database = "your_database"; // Change this to your MySQL database name
    
    $conn = new mysqli($servername, $username, $password, $database);
    
    // Check connection
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }
    
    // Get form data
    $username = $_POST['first'];
    $password = $_POST['password'];
    $user_type = $_POST['user_type']; // Assuming you have added this to your form
    
    // Prepare SQL statement to insert data into the database
    $sql = "INSERT INTO users (username, password, user_type) VALUES ('$username', '$password', '$user_type')";
    
    if ($conn->query($sql) === TRUE) {
        echo "New record created successfully";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
    
    // Close database connection
    $conn->close();
}
?>
