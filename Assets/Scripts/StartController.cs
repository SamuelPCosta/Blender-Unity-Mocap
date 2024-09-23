using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using TMPro;

public class StartController : MonoBehaviour
{
    [Header("Start")]
    public GameObject start;
    public TextMeshProUGUI seconds;

    public bool isConverting = false;

    void Update(){
        Vector3 screenPosition = Camera.main.WorldToScreenPoint(start.transform.position);

        float screenHeight = Screen.height;
        if (screenPosition.y >= screenHeight * 0.85f && start.activeSelf)
        {
            if (!isConverting){
                StopAllCoroutines();
                isConverting = false;
                StartCoroutine(StartTimer());
            }
            //else
            //    StartCoroutine(Stop());
        }
    }

    private IEnumerator StartTimer()
    {
        ClearLog();
        Debug.Log("Start in 3");
        seconds.text = "3";
        yield return new WaitForSeconds(1f);
        ClearLog();
        Debug.Log("Start in 2");
        seconds.text = "2";
        yield return new WaitForSeconds(1f);
        ClearLog();
        Debug.Log("Start in 1");
        seconds.text = "1";
        yield return new WaitForSeconds(1f);
        ClearLog();
        Debug.Log("Start");
        seconds.text = "";
        isConverting = true;
        transform.parent.GetComponent<MovementController>().setTare();
    }

    //private IEnumerator Stop()
    //{
    //    ClearLog();
    //    Debug.Log("Stop");
    //    seconds.text = "Stop";
    //    yield return new WaitForSeconds(3f);
    //    Debug.Log("Reset");
    //    //seconds.text = "Start again";
    //    transform.parent.GetComponent<MovementController>().setFalse();
    //}

    public static void ClearLog()
    {
        var assembly = System.Reflection.Assembly.GetAssembly(typeof(SceneView));
        var logEntries = assembly.GetType("UnityEditor.LogEntries");
        var clearMethod = logEntries.GetMethod("Clear");
        clearMethod.Invoke(null, null);
    }
}
