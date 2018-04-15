using UnityEngine;

public class PuckControllerBlue : MonoBehaviour {

    public Rigidbody2D puckBody;
    private Vector2 startPoint;

    private bool isControllable;
    private bool isBoosting;
    private float moveForce;
    private float boostMultiplier;
   
    
    public int Score { get; set; }

	// Use this for initialization
	void Start () {
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
    void Update () {
        if (isControllable)
        {
            Movement();
        }
	}

    void Movement()
    {
        if (Input.GetKey(KeyCode.LeftShift))
        {
            isBoosting = true;
            moveForce *= boostMultiplier;
        }
        if (Input.GetKey(KeyCode.W))
        {
            //puckBody.velocity = Vector2.up * 10;
            puckBody.AddForce(Vector2.up * moveForce, ForceMode2D.Impulse);
        }
        if (Input.GetKey(KeyCode.A))
        {
            puckBody.AddForce(Vector2.left * moveForce, ForceMode2D.Impulse);
        }
        if (Input.GetKey(KeyCode.S))
        {
            puckBody.AddForce(Vector2.down * moveForce, ForceMode2D.Impulse);
        }
        if (Input.GetKey(KeyCode.D))
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
        if (col.gameObject.tag == "TopGoal")
        {
            isControllable = false;
            puckBody.AddForce(Vector2.up * 500, ForceMode2D.Force);
        }
    }

    private void OnTriggerExit2D(Collider2D col)
    {
        if(col.gameObject.tag == "TopGoal")
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
