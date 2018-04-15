using UnityEngine;

public class PuckControllerRed : MonoBehaviour
{

    public Rigidbody2D puckBody;
    private Vector2 startPoint;

    private bool isControllable;
    private bool isBoosting;
    private float moveForce;
    private float boostMultiplier;


    public int Score { get; set; }

    // Use this for initialization
    void Start()
    {
        startPoint = puckBody.position;
        boostMultiplier = 2;
        Score = 0;
        MyReset();
    }

    void MyReset()
    {
        puckBody.position = startPoint;
        puckBody.velocity = Vector2.zero;
        moveForce = 2f;
        isControllable = true;
    }

    // Update is called once per frame
    void Update()
    {
        if (isControllable)
        {
            Movement();
        }
    }

    void Movement()
    {
        if (Input.GetKeyDown(KeyCode.Alpha0))
        {
            isBoosting = true;
            moveForce *= boostMultiplier;
        }
        if (Input.GetKey(KeyCode.UpArrow))
        {
            //puckBody.velocity = Vector2.up * 10;
            puckBody.AddForce(Vector2.up * moveForce, ForceMode2D.Impulse);
        }
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            puckBody.AddForce(Vector2.left * moveForce, ForceMode2D.Impulse);
        }
        if (Input.GetKey(KeyCode.DownArrow))
        {
            puckBody.AddForce(Vector2.down * moveForce, ForceMode2D.Impulse);
        }
        if (Input.GetKey(KeyCode.RightArrow))
        {
            puckBody.AddForce(Vector2.right * moveForce, ForceMode2D.Impulse);
        }

        if (isBoosting && !Input.GetKey(KeyCode.LeftShift))
        {
            moveForce /= boostMultiplier;
            isBoosting = false;
        }
    }

    private void OnCollisionEnter2D(Collision2D col)
    {
    }

    private void OnTriggerEnter2D(Collider2D col)
    {
        if (col.gameObject.tag == "BottomGoal")
        {
            isControllable = false;
            puckBody.AddForce(Vector2.down * 500, ForceMode2D.Force);
        }
    }

    private void OnTriggerExit2D(Collider2D col)
    {
        if (col.gameObject.tag == "BottomGoal")
        {
            MyReset();
            Score--; ;
        }
        if (col.gameObject.tag == "Arena")
        {
            MyReset();
        }
    }


}
